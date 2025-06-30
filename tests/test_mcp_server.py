import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from todoist_mcp_server import todoist
from todoist_mcp_server.todoist_client import TodoistClient


class TestMCPServerEndpoints:
    """Test cases for MCP Server endpoints"""

    @pytest.fixture
    def mock_client(self):
        """Mock TodoistClient for testing"""
        mock = AsyncMock(spec=TodoistClient)
        return mock

    @pytest.mark.asyncio
    async def test_create_task_success(self, mock_client, sample_task_data):
        """Test successful task creation via MCP endpoint"""
        mock_client.find_project_by_name.return_value = "123"
        mock_client.create_task.return_value = sample_task_data
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.create_task(
                content="Test task",
                description="Test description",
                project_name="Work",
                due_string="tomorrow",
                priority=2,
                labels=["test"]
            )
        
        assert result["success"] is True
        assert result["task"] == sample_task_data
        assert "Test task" in result["message"]
        mock_client.create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task_minimal_params(self, mock_client, sample_task_data):
        """Test task creation with minimal parameters"""
        mock_client.create_task.return_value = sample_task_data
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.create_task(content="Simple task")
        
        assert result["success"] is True
        assert result["task"] == sample_task_data
        mock_client.create_task.assert_called_once_with(
            content="Simple task",
            description="",
            project_id=None,
            due_string=None,
            priority=1,
            labels=None
        )

    @pytest.mark.asyncio
    async def test_create_task_project_not_found_uses_inbox(self, mock_client, sample_task_data):
        """Test task creation when project not found, falls back to Inbox"""
        mock_client.find_project_by_name.side_effect = [None, "inbox_id"]  # Project not found, then Inbox found
        mock_client.create_task.return_value = sample_task_data
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.create_task(
                content="Test task",
                project_name="NonExistent"
            )
        
        assert result["success"] is True
        # Should have called find_project_by_name twice: once for the project, once for Inbox
        assert mock_client.find_project_by_name.call_count == 2
        mock_client.create_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task_no_inbox_error(self, mock_client):
        """Test task creation when neither project nor Inbox found"""
        mock_client.find_project_by_name.return_value = None  # Neither project nor Inbox found
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.create_task(
                content="Test task",
                project_name="NonExistent"
            )
        
        assert "error" in result
        assert "Something went wrong" in result["error"]

    @pytest.mark.asyncio
    async def test_create_task_client_error(self, mock_client):
        """Test task creation with client error"""
        mock_client.create_task.return_value = {"error": "API error"}
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.create_task(content="Test task")
        
        assert "error" in result
        assert result["error"] == "API error"

    @pytest.mark.asyncio
    async def test_create_task_exception(self, mock_client):
        """Test task creation with exception"""
        mock_client.create_task.side_effect = Exception("Connection error")
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.create_task(content="Test task")
        
        assert "error" in result
        assert "Failed to create task" in result["error"]

    @pytest.mark.asyncio
    async def test_list_active_tasks_success(self, mock_client, sample_tasks_list):
        """Test successful active tasks listing"""
        mock_client.get_tasks.return_value = sample_tasks_list
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.list_active_tasks()
        
        assert result["success"] is True
        assert result["tasks"] == sample_tasks_list
        assert result["count"] == len(sample_tasks_list)
        assert "Found 2 tasks" in result["message"]

    @pytest.mark.asyncio
    async def test_list_active_tasks_with_project_name(self, mock_client, sample_tasks_list):
        """Test active tasks listing with project name"""
        mock_client.find_project_by_name.return_value = "123"
        mock_client.get_tasks.return_value = sample_tasks_list
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.list_active_tasks(
                project_name="Work",
                limit=10
            )
        
        assert result["success"] is True
        mock_client.find_project_by_name.assert_called_once_with("Work")
        mock_client.get_tasks.assert_called_once_with(
            project_id="123",
            filter_string=None,
            limit=10
        )

    @pytest.mark.asyncio
    async def test_list_active_tasks_project_not_found_uses_inbox(self, mock_client, sample_tasks_list):
        """Test active tasks listing when project not found, uses Inbox with limit 5"""
        mock_client.find_project_by_name.side_effect = [None, "inbox_id"]
        mock_client.get_tasks.return_value = sample_tasks_list
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.list_active_tasks(project_name="NonExistent")
        
        assert result["success"] is True
        # Should have called get_tasks with inbox_id and limit 5
        mock_client.get_tasks.assert_called_once_with(
            project_id="inbox_id",
            filter_string=None,
            limit=5
        )

    @pytest.mark.asyncio
    async def test_list_active_tasks_no_inbox_error(self, mock_client):
        """Test active tasks listing when neither project nor Inbox found"""
        mock_client.find_project_by_name.return_value = None
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.list_active_tasks(project_name="NonExistent")
        
        assert "error" in result
        assert "Something went wrong" in result["error"]

    @pytest.mark.asyncio
    async def test_list_active_tasks_with_filter(self, mock_client, sample_tasks_list):
        """Test active tasks listing with filter string"""
        mock_client.get_tasks.return_value = sample_tasks_list
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.list_active_tasks(
                filter_string="today",
                limit=20
            )
        
        assert result["success"] is True
        mock_client.get_tasks.assert_called_once_with(
            project_id=None,
            filter_string="today",
            limit=20
        )

    @pytest.mark.asyncio
    async def test_list_active_tasks_client_error(self, mock_client):
        """Test active tasks listing with client error"""
        mock_client.get_tasks.return_value = {"error": "API error"}
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.list_active_tasks()
        
        assert "error" in result
        assert result["error"] == "API error"

    @pytest.mark.asyncio
    async def test_list_active_tasks_exception(self, mock_client):
        """Test active tasks listing with exception"""
        mock_client.get_tasks.side_effect = Exception("Connection error")
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.list_active_tasks()
        
        assert "error" in result
        assert "Failed to list tasks" in result["error"]

    @pytest.mark.asyncio
    async def test_list_completed_tasks_success(self, mock_client, sample_completed_tasks):
        """Test successful completed tasks listing"""
        mock_client.get_completed_tasks.return_value = sample_completed_tasks
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.list_completed_tasks()
        
        assert result["success"] is True
        assert result["completed_tasks"] == sample_completed_tasks["items"]
        assert result["count"] == 2
        assert "Found 2 completed tasks" in result["message"]

    @pytest.mark.asyncio
    async def test_list_completed_tasks_with_project(self, mock_client, sample_completed_tasks):
        """Test completed tasks listing with project name"""
        mock_client.find_project_by_name.return_value = "123"
        mock_client.get_completed_tasks.return_value = sample_completed_tasks
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.list_completed_tasks(
                project_name="Work",
                since="2024-01-01",
                until="2024-01-02",
                limit=50
            )
        
        assert result["success"] is True
        mock_client.find_project_by_name.assert_called_once_with("Work")
        mock_client.get_completed_tasks.assert_called_once_with(
            project_id="123",
            since="2024-01-01",
            until="2024-01-02",
            limit=50
        )

    @pytest.mark.asyncio
    @patch('todoist_mcp_server.todoist.datetime')
    async def test_list_completed_tasks_default_timespan(self, mock_datetime, mock_client, sample_completed_tasks):
        """Test completed tasks listing with default 24-hour timespan"""
        from datetime import datetime, timedelta
        
        # Mock current time
        now = datetime(2024, 1, 2, 12, 0, 0)
        yesterday = now - timedelta(days=1)
        
        mock_datetime.now.return_value = now
        mock_client.get_completed_tasks.return_value = sample_completed_tasks
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.list_completed_tasks()
        
        assert result["success"] is True
        # Should have called with datetime parameters for last 24 hours
        mock_client.get_completed_tasks.assert_called_once()
        call_args = mock_client.get_completed_tasks.call_args[1]
        assert call_args["project_id"] is None
        assert call_args["limit"] == 30
        # since and until should be set to datetime strings
        assert "since" in call_args
        assert "until" in call_args

    @pytest.mark.asyncio
    async def test_list_completed_tasks_project_not_found_uses_inbox(self, mock_client, sample_completed_tasks):
        """Test completed tasks listing when project not found, uses Inbox"""
        mock_client.find_project_by_name.side_effect = [None, "inbox_id"]
        mock_client.get_completed_tasks.return_value = sample_completed_tasks
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.list_completed_tasks(project_name="NonExistent")
        
        assert result["success"] is True
        # Should have used inbox_id
        call_args = mock_client.get_completed_tasks.call_args[1]
        assert call_args["project_id"] == "inbox_id"

    @pytest.mark.asyncio
    async def test_list_completed_tasks_no_inbox_error(self, mock_client):
        """Test completed tasks listing when neither project nor Inbox found"""
        mock_client.find_project_by_name.return_value = None
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.list_completed_tasks(project_name="NonExistent")
        
        assert "error" in result
        assert "Something went wrong" in result["error"]

    @pytest.mark.asyncio
    async def test_list_completed_tasks_client_error(self, mock_client):
        """Test completed tasks listing with client error"""
        mock_client.get_completed_tasks.return_value = {"error": "API error"}
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.list_completed_tasks()
        
        assert "error" in result
        assert result["error"] == "API error"

    @pytest.mark.asyncio
    async def test_list_completed_tasks_exception(self, mock_client):
        """Test completed tasks listing with exception"""
        mock_client.get_completed_tasks.side_effect = Exception("Connection error")
        
        with patch('todoist_mcp_server.todoist.get_client', return_value=mock_client):
            result = await todoist.list_completed_tasks()
        
        assert "error" in result
        assert "Failed to list completed tasks" in result["error"]

    @pytest.mark.asyncio
    async def test_get_client_function(self, mock_env, reset_singleton):
        """Test the get_client helper function"""
        client = todoist.get_client()
        assert isinstance(client, TodoistClient)
        
        # Should return the same instance (singleton)
        client2 = todoist.get_client()
        assert client is client2 