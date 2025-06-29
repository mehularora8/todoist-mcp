# Todoist MCP Server

Unofficial MCP server for Todoist that allows agents to create, and list tasks in your Todoist account.

## Features

- **Create tasks** with descriptions, due dates, priorities, and labels and projects.
- **List tasks** List completed or uncompleted tasks with filtering by project or Todoist filters. 

Works with Claude Desktop, Cursor, and other MCP clients

## Installation

```bash
pip install todoist-mcp-server
```

## Setup

### 1. Get Your Todoist API Token

1. Go to [Todoist Integrations Settings](https://todoist.com/prefs/integrations)
2. Scroll down to "API token"
3. Copy your API token (keep it secure!)

### 2. Configure Your MCP Client

## Usage Examples

Here are some examples of how to use the Todoist MCP server with different clients:

### Claude Desktop

Add this to your `claude_desktop_config.json` file: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%/Claude/claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "todoist": {
      "command": "todoist-mcp-server",
      "env": {
        "TODOIST_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

#### Cursor

Add this to your Cursor settings:

1. Open Cursor Settings (`Cmd/Ctrl + ,`)
2. Search for "MCP" 
3. Add the MCP server configuration:

```json
{
  "mcpServers": {
    "todoist": {
      "command": "todoist-mcp-server",
      "env": {
        "TODOIST_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

#### Other MCP Clients

For any MCP-compatible client, use:
- **Command:** `todoist-mcp-server`
- **Environment Variable:** `TODOIST_API_TOKEN=your-token`

### 3. Restart Your Client

Restart Claude Desktop, Cursor, or your MCP client to load the server.

## Usage

Once configured, you can interact with Todoist using natural language:

### Creating Tasks
- "Create a task to buy groceries"
- "Add a task 'Call dentist' due tomorrow with high priority"
- "Create a task to finish the report with description 'Include Q4 metrics' due next Friday"

### Listing Tasks
- "Show me my tasks for today"
- "List all my high priority tasks"
- "What tasks do I have in my Work project?"



## Available Tools

### `create_task`
Create a new task in Todoist.

**Parameters:**
- `content` (required): Task title/content
- `description` (optional): Task description
- `project_name` (optional): Project name to add task to
- `due_string` (optional): Due date in natural language ("tomorrow", "next monday")
- `priority` (optional): Priority level 1-4 (1=low, 2=medium, 3=high, 4=urgent)
- `labels` (optional): List of label names

### `list_active_tasks`
List active tasks from Todoist.

**Parameters:**
- `project_name` (optional): Filter by project name
- `filter_string` (optional): Todoist filter ("today", "overdue", "p1")
- `limit` (optional): Maximum number of tasks (default: 50)

## Troubleshooting

### "Server disconnected" Error
1. Make sure you've installed the package: `pip install todoist-mcp-server`
2. Verify your API token is correct
3. Check that the config file is in the right location
4. Restart your MCP client completely

### "Command not found" or "ENOENT" Error
The most common cause is that your MCP client can't find the `todoist-mcp-server` command in its PATH.

**Solution: Use the full path to the command**

1. Find where the command is installed:
   ```bash
   which todoist-mcp-server
   ```

2. Use the full path in your MCP config:
   ```json
   {
     "mcpServers": {
       "todoist": {
         "command": "/full/path/to/todoist-mcp-server",
         "env": {
           "TODOIST_API_TOKEN": "your-api-token-here"
         }
       }
     }
   }
   ```

**Other fixes:**
- Ensure the package is installed in the same Python environment your MCP client uses
- Try reinstalling: `pip uninstall todoist-mcp-server && pip install todoist-mcp-server`

### API Token Issues
- Get a fresh token from [Todoist Integrations](https://todoist.com/prefs/integrations)
- Make sure there are no extra spaces in your config file
- Verify the token has the necessary permissions

## Development

To contribute or run from source:

```bash
git clone https://github.com/mehularora8/todoist-mcp
cd todoist-mcp
pip install -e .
```

## Security

- Your API token is stored locally and only used to communicate with Todoist's API
- No data is sent to third parties
- The MCP server runs locally on your machine

## License

MIT License - see LICENSE file for details.

## Support

- 🐛 **Issues:** Report bugs or request features
- 📖 **Todoist API:** [Official Documentation](https://developer.todoist.com/rest/v2/)
- 🔧 **MCP Protocol:** [Model Context Protocol](https://modelcontextprotocol.io/)

---

**Note:** This is an unofficial integration and is not affiliated with Todoist or Doist Inc.
