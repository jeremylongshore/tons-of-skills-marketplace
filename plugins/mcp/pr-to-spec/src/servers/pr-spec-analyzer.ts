#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
import {
	analyzeAssumptions,
	buildEnvelope,
	buildLocalDiffSource,
	classifyRisks,
	createClient,
	createEmptyGraph,
	detectDriftWithSpec,
	evaluateContracts,
	evaluateGate,
	fetchPR,
	generateSpec,
	githubPRtoDiffSource,
	readContracts,
	readIntent,
	readPolicy,
	writeIntent,
} from "../index.js";

// ---------------------------------------------------------------------------
// Input schemas
// ---------------------------------------------------------------------------

const AnalyzePRSchema = z.object({
	repo: z.string().describe("GitHub repo in owner/name format, e.g. 'facebook/react'"),
	pr: z.number().int().positive().describe("Pull request number"),
});

const ScanLocalSchema = z.object({
	repoPath: z.string().describe("Absolute path to the local git repository"),
	branch: z.string().optional().describe("Base branch to diff against (default: main)"),
	staged: z.boolean().optional().describe("Only scan staged changes"),
	commits: z
		.number()
		.int()
		.positive()
		.optional()
		.describe("Number of recent commits to scan (e.g. 3 for HEAD~3)"),
});

const CheckDriftSchema = z.object({
	repoPath: z.string().describe("Absolute path to the local git repository"),
	branch: z.string().optional().describe("Base branch to diff against (default: main)"),
	staged: z.boolean().optional().describe("Only check staged changes"),
});

const SetIntentSchema = z.object({
	repoPath: z.string().describe("Absolute path to the local git repository"),
	goal: z.string().min(1).describe("What this change is supposed to accomplish"),
	scope: z
		.array(z.string())
		.optional()
		.describe("Glob patterns for expected file scope, e.g. ['src/api/**']"),
	forbid: z
		.array(z.string())
		.optional()
		.describe("Glob patterns for forbidden files, e.g. ['src/db/**']"),
	maxRisk: z.enum(["low", "medium", "high"]).optional().describe("Maximum acceptable risk level"),
	type: z
		.enum(["feature", "bugfix", "refactor", "docs", "test", "chore", "config", "mixed"])
		.optional()
		.describe("Expected change type"),
	sizeBudget: z.number().int().positive().optional().describe("Maximum total LOC changes allowed"),
});

const ShowIntentSchema = z.object({
	repoPath: z.string().describe("Absolute path to the local git repository"),
});

const AnalyzeAssumptionsSchema = z.object({
	repoPath: z.string().describe("Absolute path to the local git repository"),
	branch: z.string().optional().describe("Base branch to diff against (default: main)"),
	staged: z.boolean().optional().describe("Only analyze staged changes"),
});

// ---------------------------------------------------------------------------
// Tool implementations
// ---------------------------------------------------------------------------

async function analyzePR(args: z.infer<typeof AnalyzePRSchema>) {
	const token = process.env.GITHUB_TOKEN;
	if (!token) {
		throw new Error("GitHub token required. Set GITHUB_TOKEN in the MCP server environment.");
	}

	const [owner, repo] = args.repo.split("/");
	if (!owner || !repo) {
		throw new Error("repo must be in owner/name format, e.g. 'facebook/react'");
	}

	const client = createClient(token);
	const prData = await fetchPR(client, owner, repo, args.pr);
	const diffSource = githubPRtoDiffSource(prData, args.repo);
	const spec = generateSpec(diffSource, args.repo);
	const risks = classifyRisks(diffSource.files);
	const envelope = buildEnvelope("analyze_pr", spec);

	return envelope;
}

function scanLocal(args: z.infer<typeof ScanLocalSchema>) {
	const diffSource = buildLocalDiffSource({
		cwd: args.repoPath,
		base: args.branch,
		staged: args.staged,
		commits: args.commits,
	});

	const spec = generateSpec(diffSource);
	const envelope = buildEnvelope("scan_local", spec);

	return envelope;
}

function checkDrift(args: z.infer<typeof CheckDriftSchema>) {
	const intent = readIntent(args.repoPath);
	if (!intent) {
		throw new Error(
			"No intent declared. Use set_intent first to declare what this change should do.",
		);
	}

	const diffSource = buildLocalDiffSource({
		cwd: args.repoPath,
		base: args.branch,
		staged: args.staged,
	});

	const spec = generateSpec(diffSource);
	const signals = detectDriftWithSpec(diffSource, intent, spec.intent.change_type, spec.risk_flags);

	// Evaluate contracts if defined
	const contracts = readContracts(args.repoPath);
	const contractResults =
		contracts.length > 0 ? evaluateContracts(contracts, diffSource, spec) : undefined;

	// Evaluate gate if policy is defined
	const policy = readPolicy(args.repoPath);
	let gateResult = undefined;
	if (policy) {
		// Gate requires a graph; create a minimal empty graph for standalone use
		const emptyGraph = createEmptyGraph();
		gateResult = evaluateGate(emptyGraph, intent, diffSource, policy, contractResults);
	}

	const envelope = buildEnvelope("check_drift", spec, {
		signals,
		intent,
		gate_result: gateResult,
		contracts: contractResults,
	});

	return envelope;
}

function setIntent(args: z.infer<typeof SetIntentSchema>) {
	const intent = {
		goal: args.goal,
		expected_scope: args.scope ?? [],
		forbidden_scope: args.forbid ?? [],
		max_risk: args.maxRisk ?? ("high" as const),
		expected_type: args.type,
		size_budget: args.sizeBudget,
		status: "draft" as const,
		created_at: new Date().toISOString(),
		updated_at: new Date().toISOString(),
	};

	writeIntent(intent, args.repoPath);

	return {
		status: "ok",
		message: `Intent saved to ${args.repoPath}/.pr-to-spec/intent.yaml`,
		intent,
	};
}

function showIntent(args: z.infer<typeof ShowIntentSchema>) {
	const intent = readIntent(args.repoPath);
	if (!intent) {
		return {
			status: "none",
			message: "No intent declared for this repository.",
		};
	}
	return { status: "ok", intent };
}

function analyzeAssumptionsTool(args: z.infer<typeof AnalyzeAssumptionsSchema>) {
	const intent = readIntent(args.repoPath);
	if (!intent) {
		throw new Error(
			"No intent declared. Use set_intent first to declare what this change should do.",
		);
	}

	const diffSource = buildLocalDiffSource({
		cwd: args.repoPath,
		base: args.branch,
		staged: args.staged,
	});

	const decisions = analyzeAssumptions(diffSource, intent);
	const spec = generateSpec(diffSource);

	return {
		decisions,
		summary: {
			total: decisions.length,
			must_ask: decisions.filter((d) => d.action === "must_ask").length,
			confirm_upfront: decisions.filter((d) => d.action === "confirm_upfront").length,
			ask_adhoc: decisions.filter((d) => d.action === "ask_adhoc").length,
			assume_safe: decisions.filter((d) => d.action === "assume_safe").length,
		},
		spec_summary: spec.summary,
	};
}

// ---------------------------------------------------------------------------
// MCP Server setup
// ---------------------------------------------------------------------------

const server = new Server(
	{
		name: "pr-spec-analyzer",
		version: "0.8.1",
	},
	{
		capabilities: {
			tools: {},
		},
	},
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
	return {
		tools: [
			{
				name: "analyze_pr",
				description:
					"Analyze a GitHub pull request and generate a structured spec with risk assessment and agent protocol envelope",
				inputSchema: {
					type: "object" as const,
					properties: {
						repo: {
							type: "string",
							description: "GitHub repo in owner/name format, e.g. 'facebook/react'",
						},
						pr: {
							type: "number",
							description: "Pull request number",
						},
					},
					required: ["repo", "pr"],
				},
			},
			{
				name: "scan_local",
				description:
					"Scan local git changes (branch diff, staged, or recent commits) and generate a structured spec with risk assessment",
				inputSchema: {
					type: "object" as const,
					properties: {
						repoPath: {
							type: "string",
							description: "Absolute path to the local git repository",
						},
						branch: {
							type: "string",
							description: "Base branch to diff against (default: main)",
						},
						staged: {
							type: "boolean",
							description: "Only scan staged changes",
						},
						commits: {
							type: "number",
							description: "Number of recent commits to scan (e.g. 3 for HEAD~3)",
						},
					},
					required: ["repoPath"],
				},
			},
			{
				name: "check_drift",
				description:
					"Check current changes against declared intent for scope creep, forbidden file access, risk escalation, and assumption violations",
				inputSchema: {
					type: "object" as const,
					properties: {
						repoPath: {
							type: "string",
							description: "Absolute path to the local git repository",
						},
						branch: {
							type: "string",
							description: "Base branch to diff against (default: main)",
						},
						staged: {
							type: "boolean",
							description: "Only check staged changes",
						},
					},
					required: ["repoPath"],
				},
			},
			{
				name: "set_intent",
				description:
					"Declare what a code change is supposed to accomplish — sets goal, scope, forbidden areas, max risk, and size budget",
				inputSchema: {
					type: "object" as const,
					properties: {
						repoPath: {
							type: "string",
							description: "Absolute path to the local git repository",
						},
						goal: {
							type: "string",
							description: "What this change is supposed to accomplish",
						},
						scope: {
							type: "array",
							items: { type: "string" },
							description: "Glob patterns for expected file scope",
						},
						forbid: {
							type: "array",
							items: { type: "string" },
							description: "Glob patterns for forbidden files",
						},
						maxRisk: {
							type: "string",
							enum: ["low", "medium", "high"],
							description: "Maximum acceptable risk level",
						},
						type: {
							type: "string",
							enum: ["feature", "bugfix", "refactor", "docs", "test", "chore", "config", "mixed"],
							description: "Expected change type",
						},
						sizeBudget: {
							type: "number",
							description: "Maximum total LOC changes allowed",
						},
					},
					required: ["repoPath", "goal"],
				},
			},
			{
				name: "show_intent",
				description: "Show the current intent declaration for a repository",
				inputSchema: {
					type: "object" as const,
					properties: {
						repoPath: {
							type: "string",
							description: "Absolute path to the local git repository",
						},
					},
					required: ["repoPath"],
				},
			},
			{
				name: "analyze_assumptions",
				description:
					"Surface implicit assumptions in code changes using a 2x2 decision matrix (predictability vs reversibility) — identifies must_ask, confirm_upfront, ask_adhoc, and assume_safe decisions",
				inputSchema: {
					type: "object" as const,
					properties: {
						repoPath: {
							type: "string",
							description: "Absolute path to the local git repository",
						},
						branch: {
							type: "string",
							description: "Base branch to diff against (default: main)",
						},
						staged: {
							type: "boolean",
							description: "Only analyze staged changes",
						},
					},
					required: ["repoPath"],
				},
			},
		],
	};
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
	try {
		let result: unknown;

		switch (request.params.name) {
			case "analyze_pr": {
				const args = AnalyzePRSchema.parse(request.params.arguments);
				result = await analyzePR(args);
				break;
			}
			case "scan_local": {
				const args = ScanLocalSchema.parse(request.params.arguments);
				result = scanLocal(args);
				break;
			}
			case "check_drift": {
				const args = CheckDriftSchema.parse(request.params.arguments);
				result = checkDrift(args);
				break;
			}
			case "set_intent": {
				const args = SetIntentSchema.parse(request.params.arguments);
				result = setIntent(args);
				break;
			}
			case "show_intent": {
				const args = ShowIntentSchema.parse(request.params.arguments);
				result = showIntent(args);
				break;
			}
			case "analyze_assumptions": {
				const args = AnalyzeAssumptionsSchema.parse(request.params.arguments);
				result = analyzeAssumptionsTool(args);
				break;
			}
			default:
				throw new Error(`Unknown tool: ${request.params.name}`);
		}

		return {
			content: [
				{
					type: "text" as const,
					text: JSON.stringify(result, null, 2),
				},
			],
		};
	} catch (error) {
		if (error instanceof z.ZodError) {
			throw new Error(
				`Invalid arguments: ${error.issues.map((e) => `${e.path.join(".")}: ${e.message}`).join(", ")}`,
			);
		}
		throw error;
	}
});

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------

async function main() {
	const transport = new StdioServerTransport();
	await server.connect(transport);
	console.error("pr-spec-analyzer MCP Server running on stdio");
}

main().catch((error) => {
	console.error("Fatal error:", error);
	process.exit(1);
});
