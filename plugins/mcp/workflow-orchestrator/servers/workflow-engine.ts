#!/usr/bin/env node
/**
 * Workflow Orchestrator MCP Server
 * DAG-based workflow execution with parallel tasks and run history
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema, Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';

interface Task {
  id: string;
  name: string;
  command: string;
  dependencies: string[];
  status: 'pending' | 'running' | 'completed' | 'failed';
  result?: any;
  error?: string;
  startTime?: string;
  endTime?: string;
}

interface Workflow {
  id: string;
  name: string;
  tasks: Task[];
  status: 'pending' | 'running' | 'completed' | 'failed';
  createdAt: string;
  completedAt?: string;
}

const workflows = new Map<string, Workflow>();
const runHistory: Workflow[] = [];

const CreateWorkflowSchema = z.object({
  name: z.string(),
  tasks: z.array(z.object({
    id: z.string(),
    name: z.string(),
    command: z.string(),
    dependencies: z.array(z.string()).default([])
  }))
});

const ExecuteWorkflowSchema = z.object({
  workflowId: z.string(),
  parallel: z.boolean().default(true)
});

const GetWorkflowSchema = z.object({
  workflowId: z.string()
});

const ListWorkflowsSchema = z.object({
  status: z.enum(['pending', 'running', 'completed', 'failed']).optional()
});

async function createWorkflow(args: z.infer<typeof CreateWorkflowSchema>) {
  const { name, tasks } = args;

  const workflowId = `wf_${Date.now()}`;
  const workflow: Workflow = {
    id: workflowId,
    name,
    tasks: tasks.map(t => ({ ...t, status: 'pending' })),
    status: 'pending',
    createdAt: new Date().toISOString()
  };

  workflows.set(workflowId, workflow);

  return {
    workflowId,
    name,
    totalTasks: tasks.length,
    created: true
  };
}

async function executeWorkflow(args: z.infer<typeof ExecuteWorkflowSchema>) {
  const { workflowId, parallel } = args;

  const workflow = workflows.get(workflowId);
  if (!workflow) throw new Error(`Workflow not found: ${workflowId}`);

  workflow.status = 'running';

  // Execute tasks (simplified - real implementation would use child_process)
  for (const task of workflow.tasks) {
    const canRun = task.dependencies.every(depId => {
      const dep = workflow.tasks.find(t => t.id === depId);
      return dep?.status === 'completed';
    });

    if (canRun) {
      task.status = 'running';
      task.startTime = new Date().toISOString();

      try {
        // Simulate task execution
        task.result = { output: `Executed: ${task.command}` };
        task.status = 'completed';
      } catch (error) {
        task.status = 'failed';
        task.error = String(error);
      }

      task.endTime = new Date().toISOString();
    }
  }

  workflow.status = workflow.tasks.every(t => t.status === 'completed') ? 'completed' : 'failed';
  workflow.completedAt = new Date().toISOString();

  runHistory.push({ ...workflow });

  return {
    workflowId,
    status: workflow.status,
    completedTasks: workflow.tasks.filter(t => t.status === 'completed').length,
    failedTasks: workflow.tasks.filter(t => t.status === 'failed').length
  };
}

async function getWorkflow(args: z.infer<typeof GetWorkflowSchema>) {
  const { workflowId } = args;
  const workflow = workflows.get(workflowId);
  if (!workflow) throw new Error(`Workflow not found: ${workflowId}`);
  return workflow;
}

async function listWorkflows(args: z.infer<typeof ListWorkflowsSchema>) {
  const { status } = args;
  let list = Array.from(workflows.values());

  if (status) {
    list = list.filter(w => w.status === status);
  }

  return {
    workflows: list.map(w => ({
      id: w.id,
      name: w.name,
      status: w.status,
      totalTasks: w.tasks.length,
      createdAt: w.createdAt
    })),
    total: list.length
  };
}

const server = new Server({ name: 'workflow-engine', version: '1.0.0' }, { capabilities: { tools: {} } });

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    { name: 'create_workflow', description: 'Create DAG workflow', inputSchema: z.toJSONSchema(CreateWorkflowSchema, { target: 'draft-07', io: 'input' }) as Tool['inputSchema'] },
    { name: 'execute_workflow', description: 'Execute workflow', inputSchema: z.toJSONSchema(ExecuteWorkflowSchema, { target: 'draft-07', io: 'input' }) as Tool['inputSchema'] },
    { name: 'get_workflow', description: 'Get workflow status', inputSchema: z.toJSONSchema(GetWorkflowSchema, { target: 'draft-07', io: 'input' }) as Tool['inputSchema'] },
    { name: 'list_workflows', description: 'List workflows', inputSchema: z.toJSONSchema(ListWorkflowsSchema, { target: 'draft-07', io: 'input' }) as Tool['inputSchema'] }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  try {
    let result;
    if (name === 'create_workflow') result = await createWorkflow(CreateWorkflowSchema.parse(args));
    else if (name === 'execute_workflow') result = await executeWorkflow(ExecuteWorkflowSchema.parse(args));
    else if (name === 'get_workflow') result = await getWorkflow(GetWorkflowSchema.parse(args));
    else if (name === 'list_workflows') result = await listWorkflows(ListWorkflowsSchema.parse(args));
    else throw new Error(`Unknown tool: ${name}`);
    return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
  } catch (error) {
    return { content: [{ type: 'text', text: JSON.stringify({ error: error instanceof Error ? error.message : String(error) }, null, 2) }], isError: true };
  }
});

async function main() {
  await server.connect(new StdioServerTransport());
  console.error('Workflow Orchestrator MCP server running');
}

main().catch(err => { console.error(err); process.exit(1); });
