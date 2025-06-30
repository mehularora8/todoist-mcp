import pytest
import httpx
import respx
from unittest.mock import AsyncMock, patch
from todoist_mcp_server.todoist_client import TodoistClient


class TestTodoistClient:
    """Test cases for TodoistClient"""

    def test_client_requires_api_token(self, reset_singleton):
        """Test that client raises error when API token is missing"""
        with pytest.raises(ValueError, match="TODOIST_API_TOKEN environment variable is required"):
            TodoistClient()

    def test_client_singleton_pattern(self, mock_env, reset_singleton):
        """Test that TodoistClient follows singleton pattern"""
        client1 = TodoistClient()
        client2 = TodoistClient()
        assert client1 is client2

    def test_client_initialization(self, mock_env, mock_api_token, reset_singleton):
        """Test proper client initialization"""
        client = TodoistClient()
        assert client.api_token == mock_api_token
        assert client.base_url == "https://api.todoist.com/api/v1"
        assert client.headers["Authorization"] == f"Bearer {mock_api_token}"

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_projects_success(self, mock_env, sample_project_data, reset_singleton):
        """Test successful projects retrieval"""
        respx.get("https://api.todoist.com/api/v1/projects").mock(
            return_value=httpx.Response(200, json=sample_project_data)
        )
        
        client = TodoistClient()
        result = await client.get_projects()
        
        assert result == sample_project_data
        assert len(result) == 3

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_projects_error(self, mock_env, reset_singleton):
        """Test projects retrieval with HTTP error"""
        respx.get("https://api.todoist.com/api/v1/projects").mock(
            return_value=httpx.Response(401, json={"error": "Unauthorized"})
        )
        
        client = TodoistClient()
        result = await client.get_projects()
        
        assert "error" in result
        assert "HTTP error" in result["error"]

    @pytest.mark.asyncio
    async def test_find_project_by_name_success(self, mock_env, sample_project_data, reset_singleton):
        """Test finding project by name successfully"""
        client = TodoistClient()
        
        with patch.object(client, 'get_projects', return_value=sample_project_data):
            project_id = await client.find_project_by_name("Work")
            assert project_id == "123"
            
        with patch.object(client, 'get_projects', return_value=sample_project_data):
            project_id = await client.find_project_by_name("work")  # case insensitive
            assert project_id == "123"

    @pytest.mark.asyncio
    async def test_find_project_by_name_not_found(self, mock_env, sample_project_data, reset_singleton):
        """Test finding project by name when not found"""
        client = TodoistClient()
        
        with patch.object(client, 'get_projects', return_value=sample_project_data):
            project_id = await client.find_project_by_name("NonExistent")
            assert project_id is None

    @pytest.mark.asyncio
    async def test_find_project_by_name_error(self, mock_env, reset_singleton):
        """Test finding project by name with API error"""
        client = TodoistClient()
        
        with patch.object(client, 'get_projects', return_value={"error": "API error"}):
            project_id = await client.find_project_by_name("Work")
            assert project_id is None

    @pytest.mark.asyncio
    @respx.mock
    async def test_create_task_success(self, mock_env, sample_task_data, reset_singleton):
        """Test successful task creation"""
        respx.post("https://api.todoist.com/api/v1/tasks").mock(
            return_value=httpx.Response(200, json=sample_task_data)
        )
        
        client = TodoistClient()
        result = await client.create_task(
            content="Test task",
            description="Test description",
            project_id="123",
            priority=2,
            labels=["test"]
        )
        
        assert result == sample_task_data
        assert result["content"] == "Test task"

    @pytest.mark.asyncio
    @respx.mock
    async def test_create_task_minimal(self, mock_env, reset_singleton):
        """Test task creation with minimal parameters"""
        expected_response = {"id": "task_123", "content": "Simple task"}
        respx.post("https://api.todoist.com/api/v1/tasks").mock(
            return_value=httpx.Response(200, json=expected_response)
        )
        
        client = TodoistClient()
        result = await client.create_task(content="Simple task")
        
        assert result == expected_response

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_tasks_success(self, mock_env, sample_tasks_list, reset_singleton):
        """Test successful tasks retrieval"""
        respx.get("https://api.todoist.com/api/v1/tasks").mock(
            return_value=httpx.Response(200, json=sample_tasks_list)
        )
        
        client = TodoistClient()
        result = await client.get_tasks()
        
        assert result == sample_tasks_list
        assert len(result) == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_tasks_with_filters(self, mock_env, sample_tasks_list, reset_singleton):
        """Test tasks retrieval with filters"""
        respx.get("https://api.todoist.com/api/v1/tasks").mock(
            return_value=httpx.Response(200, json=sample_tasks_list)
        )
        
        client = TodoistClient()
        result = await client.get_tasks(
            project_id="123",
            filter_string="today",
            limit=10
        )
        
        assert result == sample_tasks_list

    @pytest.mark.asyncio
    @respx.mock
    async def test_complete_task_success(self, mock_env, reset_singleton):
        """Test successful task completion"""
        respx.post("https://api.todoist.com/api/v1/tasks/task_123/close").mock(
            return_value=httpx.Response(204)
        )
        
        client = TodoistClient()
        result = await client.complete_task("task_123")
        
        assert result == {"success": True}

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_completed_tasks_success(self, mock_env, sample_completed_tasks, reset_singleton):
        """Test successful completed tasks retrieval"""
        respx.get("https://api.todoist.com/api/v1/tasks/completed/by_completion_date").mock(
            return_value=httpx.Response(200, json=sample_completed_tasks)
        )
        
        client = TodoistClient()
        result = await client.get_completed_tasks()
        
        assert result == sample_completed_tasks
        assert len(result["items"]) == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_get_completed_tasks_with_params(self, mock_env, sample_completed_tasks, reset_singleton):
        """Test completed tasks retrieval with parameters"""
        respx.get("https://api.todoist.com/api/v1/tasks/completed/by_completion_date").mock(
            return_value=httpx.Response(200, json=sample_completed_tasks)
        )
        
        client = TodoistClient()
        result = await client.get_completed_tasks(
            project_id="123",
            since="2024-01-01",
            until="2024-01-02",
            limit=100
        )
        
        assert result == sample_completed_tasks

    @pytest.mark.asyncio
    @respx.mock
    async def test_make_request_unsupported_method(self, mock_env, reset_singleton):
        """Test unsupported HTTP method"""
        client = TodoistClient()
        result = await client._make_request("PATCH", "tasks")
        
        assert "error" in result
        assert "Unsupported HTTP method" in result["error"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_make_request_network_error(self, mock_env, reset_singleton):
        """Test network error handling"""
        respx.get("https://api.todoist.com/api/v1/tasks").mock(
            side_effect=httpx.ConnectError("Connection failed")
        )
        
        client = TodoistClient()
        result = await client._make_request("GET", "tasks")
        
        assert "error" in result
        assert "HTTP error" in result["error"] 