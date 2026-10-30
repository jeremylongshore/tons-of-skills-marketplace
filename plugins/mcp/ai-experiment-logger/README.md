# AI Experiment Logger

**Track, analyze, and optimize your AI experiments with a comprehensive logging system featuring both MCP tools and a beautiful web dashboard.**

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Overview

The AI Experiment Logger helps you systematically track experiments across different AI tools (ChatGPT, Claude, Gemini, etc.), analyze effectiveness patterns, and make data-driven decisions about which tools and prompting strategies work best for your use cases.

**Key Features:**

- 🎯 **Structured Experiment Logging** - Capture tool, prompt, result, rating, and tags
- 📊 **Rich Statistics Dashboard** - Visualize tool performance, rating distribution, and trends
- 🔍 **Advanced Search & Filtering** - Find experiments by any field or search term
- 📈 **Performance Analytics** - Track which AI tools perform best for your needs
- 💾 **Data Persistence** - Local JSON storage with CSV export capability
- 🌐 **Dual Interface** - MCP tools for Claude Code + web UI for visual exploration
- 🎨 **Modern UI** - Clean, responsive interface built with Tailwind CSS

## What's Included

This plugin provides **7 MCP tools** for experiment management:

| Tool | Description |
|------|-------------|
| `log_experiment` | Create a new experiment entry with tool, prompt, result, and rating |
| `list_experiments` | List all experiments with optional filtering and search |
| `get_experiment` | Retrieve a specific experiment by ID |
| `update_experiment` | Modify an existing experiment |
| `delete_experiment` | Remove an experiment from the log |
| `get_statistics` | Generate comprehensive analytics and performance metrics |
| `export_experiments` | Export all data to CSV format |

## Installation

### 1. Copy the Plugin

The tracked plugin includes a self-contained `dist/index.js` stdio server.
Copy the tracked plugin directory, and use
Node.js **22.12 or newer**. No dependency installation or build is needed for
this manual stdio launch. Keep `package.json` with the entrypoint; it declares
ES modules.

### 2. Locate the Entrypoint

Use the absolute path to `dist/index.js` in your copied plugin directory in the
manual MCP configuration below. Installation does not automatically register
or start this server.

### 3. Configure MCP Server

For Claude Code, explicitly register the manual entry with the supported CLI
(substitute the absolute path to your copied or installed plugin):

```bash
claude mcp add --transport stdio --scope user ai-experiment-logger -- node "/absolute/path/to/ai-experiment-logger/dist/index.js"
```

See the [Claude Code MCP setup reference](https://code.claude.com/docs/en/mcp#option-3-add-a-local-stdio-server)
for scopes and configuration. The command above is a registration example; copying
or installing the plugin alone does not run it.

For another MCP host, use its documented configuration location with this generic
stdio configuration:

```json
{
  "mcpServers": {
    "ai-experiment-logger": {
      "command": "node",
      "args": [
        "/absolute/path/to/plugins/mcp/ai-experiment-logger/dist/index.js"
      ]
    }
  }
}
```

**Important:** Replace `/absolute/path/to` with your actual installation path.

### 4. Restart Claude Code

Restart Claude Code to load the MCP server.

## Usage

### Using MCP Tools (in Claude Code)

#### Log an Experiment

```
Use the log_experiment tool to record:
- AI Tool: "ChatGPT o1-preview"
- Prompt: "Write a Python function to calculate Fibonacci numbers recursively"
- Result: "Provided clean recursive implementation with base cases. Included time complexity analysis (O(2^n))."
- Rating: 4
- Tags: ["code-generation", "python", "algorithms"]
```

#### List Recent Experiments

```
Use the list_experiments tool to show my last 10 experiments
```

#### Search Experiments

```
Use the list_experiments tool with searchQuery="code-generation" to find all coding experiments
```

#### Get Statistics

```
Use the get_statistics tool to show me which AI tools perform best
```

#### Export Data

```
Use the export_experiments tool to generate a CSV file of all my experiments
```

### Using the Web Dashboard

#### Start the Web Server

```bash
cd plugins/mcp/ai-experiment-logger
pnpm web
```

The web UI will be available at `http://localhost:3000`

#### Web Dashboard Features

1. **Dashboard Tab**
   - View all experiments in a sortable table
   - Search across all fields in real-time
   - Filter by AI tool, rating, or date range
   - Delete experiments with confirmation

2. **Statistics Tab**
   - Total experiments and average rating
   - AI tool performance comparison
   - Rating distribution visualization
   - Top tags analysis
   - Recent activity chart (30 days)

3. **Log Experiment Button**
   - Easy form with all fields
   - Star rating selector (1-5)
   - Tag management (comma-separated)
   - Date/time picker (defaults to now)

4. **Export CSV Button**
   - Download all experiments as CSV
   - Compatible with Excel, Google Sheets, etc.
   - Includes all metadata

## Data Storage

Experiments are stored locally in JSON format:

- **Location:** `~/.ai-experiment-logger/experiments.json`
- **Format:** Structured JSON with full experiment history
- **Backup:** Recommended to periodically back up this file
- **Privacy:** All data stays on your local machine

## Example Workflows

### Workflow 1: Comparing AI Tools for Code Generation

```bash
# Log experiments with different tools
1. ChatGPT o1-preview - Rating: 5 - Tag: "code-generation"
2. Claude Sonnet 3.5 - Rating: 5 - Tag: "code-generation"
3. Gemini Pro - Rating: 3 - Tag: "code-generation"

# View statistics
Use get_statistics tool to see average ratings by tool

# Result: ChatGPT o1-preview and Claude tied at 5.0 avg rating
```

### Workflow 2: Tracking Prompt Engineering Improvements

```bash
# Log multiple iterations of the same task
Prompt v1: "Write a blog post about AI" → Rating: 2
Prompt v2: "Write a 500-word blog post about AI ethics for general audience" → Rating: 4
Prompt v3: "Write a 500-word blog post about AI ethics. Include real-world examples, counterarguments, and a strong conclusion. Target: general tech-savvy audience." → Rating: 5

# Tag all with "prompt-engineering" and "blog-writing"
# Review over time to identify what makes prompts effective
```

### Workflow 3: Finding Best Tool for Specific Tasks

```bash
# Tag experiments by task type
Tags: "creative-writing", "technical-writing", "code-review", "research"

# Use web dashboard to filter by tag
# Compare average ratings across tools for each category
# Make informed decisions about tool selection
```

## API Reference (Web Server)

If you're building integrations, the web server provides REST endpoints:

### POST /api/experiments

Create a new experiment

```json
{
  "aiTool": "ChatGPT",
  "prompt": "Your prompt",
  "result": "Summary of result",
  "rating": 4,
  "tags": ["tag1", "tag2"]
}
```

### GET /api/experiments

List experiments with optional query params:

- `searchQuery` - Full-text search
- `aiTool` - Filter by tool name
- `rating` - Filter by rating (1-5)
- `dateFrom` / `dateTo` - Date range filter

### GET /api/experiments/:id

Get specific experiment

### PUT /api/experiments/:id

Update experiment (send partial data)

### DELETE /api/experiments/:id

Delete experiment

### GET /api/statistics

Get comprehensive statistics

### GET /api/export

Download CSV export

## Configuration

### Environment Variables

The optional web UI is a separate developer workflow: it still requires
dependencies and a build. The committed stdio bundle does not start an HTTP
listener. This distribution fix does not validate web static-asset packaging.

```bash
# Web server port (default: 3000)
PORT=3000

# Data storage directory (default: ~/.ai-experiment-logger)
# Storage is fixed at ~/.ai-experiment-logger/experiments.json.
# DATA_DIR is not a supported override.
```

### Customization

You can modify the source code to:

- Add custom fields to experiments
- Create new statistics visualizations
- Implement additional filtering options
- Integrate with external analytics tools

## Troubleshooting

### MCP Server Not Appearing

1. Run `claude mcp get ai-experiment-logger` and check the configured absolute path
2. Verify the copied entry exists: `ls dist/index.js`
3. Check Claude Code logs for error messages
4. Restart Claude Code completely

### Web Server Won't Start

1. Check port 3000 is not in use: `lsof -i :3000`
2. Verify dependencies installed: `pnpm install`
3. Check build succeeded: `pnpm build`
4. Try a different port: `PORT=8080 pnpm web`

### Data Not Persisting

1. Check permissions on `~/.ai-experiment-logger/` directory
2. Verify JSON file is writable
3. Look for error messages in console output
4. Try manually creating the directory: `mkdir -p ~/.ai-experiment-logger`

## Development

### Project Structure

```
ai-experiment-logger/
├── src/
│   ├── index.ts           # MCP server entry point
│   ├── storage.ts         # Data persistence layer
│   ├── types.ts           # TypeScript interfaces
│   └── web/
│       ├── server.ts      # Express web server
│       └── public/
│           ├── index.html # Web UI
│           └── app.js     # Frontend JavaScript
├── dist/                  # Compiled JavaScript
├── mcp/
│   └── server.json       # MCP configuration
├── package.json
└── tsconfig.json
```

### Building from Source

```bash
# Install dependencies
pnpm install

# Build TypeScript
pnpm build

# Run isolated clean-copy stdio and storage probes (temporary home only)
pnpm test

# Watch mode (auto-rebuild on changes)
pnpm dev

# Start MCP server
pnpm start

# Start web server
pnpm web
```

### Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## Use Cases

- **Prompt Engineering Research** - Track which prompts work best across tools
- **AI Tool Evaluation** - Compare ChatGPT, Claude, Gemini, etc. for your needs
- **Team Collaboration** - Share experiment logs with team members
- **Quality Tracking** - Monitor AI output quality over time
- **Cost Optimization** - Identify most effective tools to reduce API costs
- **Documentation** - Maintain records of successful AI interactions
- **Learning & Training** - Build a knowledge base of effective prompts

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Issues:** [GitHub Issues](https://github.com/jeremylongshore/claude-code-plugins/issues)
- **Discussions:** [GitHub Discussions](https://github.com/jeremylongshore/claude-code-plugins/discussions)
- **Email:** plugins@example.com

## Changelog

### Version 1.0.0 (2025-10-13)

- Initial release
- 7 MCP tools for experiment management
- Web dashboard with statistics
- CSV export functionality
- Local JSON storage
- Tailwind CSS responsive UI

---

**Built with ❤️ for the Claude Code community**

## Data safety and recovery

The manual stdio server stores plaintext JSON under the current user's home directory. New directories use mode0700 and new/replaced files use0600 on POSIX; review permissions on older existing directories separately. This does not encrypt data or protect it from another process running as the same user.

Malformed JSON, unsupported stored shapes, symlinked storage targets and disappeared initialized data fail closed. Existing data is preserved instead of being reset. Writes use a private temporary file, file fsync and atomic replacement; filesystem and power-loss guarantees remain platform dependent. In-process writes are queued. Cooperating instances take an exclusive short-lived writer lock and reload the latest committed state before changing it. Reads reload committed data. Stop older logger processes before upgrading; they do not participate in this locking protocol.

A busy request has not written data. Stop all writers and inspect a stale `.experiments.lock` before recovering it; never delete `experiments.json` to repair startup. A cleanup warning after a completed replacement may leave a lock requiring recovery. Retrying after an uncertain transport result can still create duplicate records; this is not an exactly-once service.

CSV output quotes textual fields, escapes quotes and prefixes common formula-leading text with an apostrophe. Stored prompts/results remain unchanged. Exported text still requires appropriate handling by its downstream consumer.

The standalone bundle uses main's pinned Zod4.6.6 dependency. Its bundled SDK still includes Ajv's schema compiler; the application registers only the seven listed tools, parses tool arguments with local Zod schemas and never calls elicitation or accepts compiler options. This is an application boundary review, not a universal SDK security certification. The optional web dashboard's separate limitations remain; this repair does not start or certify an Express listener or add native MCP registration.
