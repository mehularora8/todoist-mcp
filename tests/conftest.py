import pytest
import os
from unittest.mock import AsyncMock, Mock
from todoist_mcp_server.todoist_client import TodoistClient


@pytest.fixture
def mock_api_token():
    """Provide a mock API token for testing"""
    return "test_token_12345"


@pytest.fixture
def mock_env(monkeypatch, mock_api_token):
    """Mock environment variables for testing"""
    monkeypatch.setenv("TODOIST_API_TOKEN", mock_api_token)


@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return [
        {"id": "123", "name": "Work", "color": "blue"},
        {"id": "456", "name": "Personal", "color": "green"},
        {"id": "789", "name": "Inbox", "color": "grey"}
    ]


@pytest.fixture
def sample_task_data():
    """Sample task data for testing"""
    return {
        "id": "task_123",
        "content": "Test task",
        "description": "Test description",
        "project_id": "123",
        "priority": 1,
        "labels": ["test"],
        "url": "https://todoist.com/app/task/task_123"
    }


@pytest.fixture
def sample_tasks_list():
    """Sample list of tasks for testing"""
    return [
        {
            "id": "task_1",
            "content": "First task",
            "project_id": "123",
            "priority": 2,
            "completed": False
        },
        {
            "id": "task_2", 
            "content": "Second task",
            "project_id": "456",
            "priority": 1,
            "completed": False
        }
    ]


@pytest.fixture
def sample_completed_tasks():
    """Sample completed tasks data for testing"""
    return {
        "items": [
            {
                "id": "completed_1",
                "content": "Completed task 1",
                "project_id": "123",
                "completed_at": "2024-01-01T10:00:00Z"
            },
            {
                "id": "completed_2",
                "content": "Completed task 2", 
                "project_id": "456",
                "completed_at": "2024-01-01T11:00:00Z"
            }
        ]
    }


@pytest.fixture
def reset_singleton():
    """Reset TodoistClient singleton for testing"""
    TodoistClient._instance = None
    TodoistClient._initialized = False
    yield
    TodoistClient._instance = None
    TodoistClient._initialized = False 