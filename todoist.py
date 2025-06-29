from typing import List
from mcp.server.fastmcp import FastMCP
from todoist_client import TodoistClient

mcp = FastMCP("todoist")


def get_client() -> TodoistClient:
    """Get Todoist client with API token from environment"""
    return TodoistClient()


@mcp.tool()
async def create_task(content: str, description: str = "", project_name: str = None, 
                      due_string: str = None, priority: int = 1, 
                     labels: List[str] = None) -> dict:
    """
    Create a new task in Todoist.

    Priorities don't map directly to Todoist priorities, but are mapped as follows:
    1 = low
    2 = medium
    3 = high
    4 = urgent

    This is done to map better to how people think about priorities.
    
    Args:
        content: The task content/title (required)
        description: Task description (optional)
        project_name: Project name to add task to
        due_string: Due date in natural language like "tomorrow", "next monday" (optional)
        priority: Priority level 1-4 (1=low, 2=medium, 3=high, 4=urgent)
        labels: List of label names to add to the task (optional)
    
    Returns:
        Dict containing the created task details or error message
    """
    try:
        client = get_client()
        
        # If project_name is provided, convert to project_id
        if project_name:
            project_id = await client.find_project_by_name(project_name)
            if not project_id:
                inbox_id = await client.find_project_by_name("Inbox")
                if not inbox_id:
                    return {"error": "Something went wrong."}
                project_id = inbox_id
        
        result = await client.create_task(
            content=content,
            description=description,
            project_id=project_id,
            due_string=due_string,
            priority=priority,
            labels=labels
        )
        
        if "error" in result:
            return result
            
        return {
            "success": True,
            "task": result,
            "url": result.get("url", ""),
            "message": f"Task '{content}' created successfully"
        }
        
    except Exception as e:
        return {"error": f"Failed to create task: {str(e)}"}


@mcp.tool()
async def list_active_tasks(project_id: str = None, project_name: str = None, 
                    filter_string: str = None, limit: int = 50) -> dict:
    """
    List tasks from Todoist
    
    Args:
        project_name: Filter tasks by project name (alternative to project_id)
        filter_string: Todoist filter string like "today", "overdue", "p1" (optional)
        limit: Maximum number of tasks to return (default 50)
    
    Returns:
        Dict containing list of tasks or error message
    """
    try:
        client = get_client()
        
        # If project_name is provided, convert to project_id
        if project_name and not project_id:
            project_id = await client.find_project_by_name(project_name)
            if not project_id:
                inbox_id = await client.find_project_by_name("Inbox")
                if not inbox_id:
                    return {"error": "Something went wrong. Please create the project first."}
                project_id = inbox_id
                limit = 5 # default to 5 if no project_id is provided, i.e. pulling from inbox
        
        result = await client.get_tasks(
            project_id=project_id,
            filter_string=filter_string,
            limit=limit
        )
        
        if "error" in result:
            return result
            
        return {
            "success": True,
            "tasks": result,
            "count": len(result),
            "message": f"Found {len(result)} tasks"
        }
        
    except Exception as e:
        return {"error": f"Failed to list tasks: {str(e)}"}


def main():
    """Run the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()

