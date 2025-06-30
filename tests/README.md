# Tests for Todoist MCP Server

## Test Coverage

Current test coverage: **96%**

- `test_todoist_client.py` - Unit tests for the TodoistClient class
- `test_mcp_server.py` - Tests for MCP server endpoints
- `conftest.py` - Pytest fixtures and configuration

## Running Tests

### Prerequisites

Install development dependencies:
```bash
uv sync --group dev
```

### Basic Test Commands

```bash
# Run all tests
python -m pytest tests/

# Run tests with verbose output
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ --cov=todoist_mcp_server --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_todoist_client.py

# Run specific test function
python -m pytest tests/test_todoist_client.py::TestTodoistClient::test_client_initialization
```

### Using the Test Runner Script

```bash
# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage

# Run with verbose output
python run_tests.py --verbose

# Run specific test
python run_tests.py --test tests/test_todoist_client.py
```

## Test Structure

### TodoistClient Tests (`test_todoist_client.py`)

Tests all client methods with mocked HTTP requests:
- Client initialization and singleton pattern
- API token validation
- Project operations (get, find by name)
- Task operations (create, get, complete)
- Completed tasks retrieval
- Error handling and network failures

### MCP Server Tests (`test_mcp_server.py`)

- `create_task` endpoint with various scenarios (missing projects, empty responses, invalid tokens)
- `list_active_tasks` endpoint with filtering
- `list_completed_tasks` endpoint with time ranges
- Project fallback logic (uses Inbox when project not found)
- Error handling and exception scenarios

## Test Data

The `conftest.py` file provides fixtures for:
- Mock API tokens
- Sample project data
- Sample task data
- Sample completed tasks data
- Environment variable mocking
- Singleton reset utilities