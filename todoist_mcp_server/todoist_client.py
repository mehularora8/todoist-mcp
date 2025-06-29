from typing import List, Dict, Optional
import httpx
import os

class TodoistClient:
    _instance = None
    _initialized = False

    def __init__(self):
        if not TodoistClient._initialized:
            api_token = os.getenv("TODOIST_API_TOKEN")
            if not api_token:
                raise ValueError("TODOIST_API_TOKEN environment variable is required")

            self.api_token = api_token
            self.base_url = "https://api.todoist.com/rest/v2"
            self.headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }

            self._http_client = None

            TodoistClient._initialized = True

    async def _get_http_client(self):
        """Get or create HTTP client with connection pooling"""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient()
        return self._http_client
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request to Todoist API"""
        url = f"{self.base_url}/{endpoint}"
        
        async with httpx.AsyncClient() as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, headers=self.headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=self.headers, json=data, params=params)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=self.headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                
                # Handle empty responses (like for task completion)
                if response.status_code == 204 or not response.content:
                    return {"success": True}
                
                return response.json()
                
            except httpx.HTTPError as e:
                return {"error": f"HTTP error: {str(e)}"}
            except Exception as e:
                return {"error": f"Request failed: {str(e)}"}

    async def get_projects(self) -> List[Dict]:
        """Get all projects"""
        result = await self._make_request("GET", "projects")
        if "error" in result:
            return result
        return result

    async def find_project_by_name(self, name: str) -> Optional[str]:
        """Find project ID by name (case-insensitive)"""
        projects = await self.get_projects()
        if "error" in projects:
            return None
        
        name_lower = name.lower()
        for project in projects:
            if project["name"].lower() == name_lower:
                return project["id"]
        return None

    async def create_task(self, content: str, description: str = "", project_id: str = None, 
                         due_string: str = None, priority: int = 1, labels: List[str] = None) -> Dict:
        """Create a new task"""
        data = {
            "content": content,
            "description": description,
            "priority": priority
        }
        
        if project_id:
            data["project_id"] = project_id
        if due_string:
            data["due_string"] = due_string
        if labels:
            data["labels"] = labels
            
        return await self._make_request("POST", "tasks", data)

    async def get_tasks(self, project_id: str = None, filter_string: str = None, limit: int = 50) -> List[Dict]:
        """Get tasks with optional filtering"""
        params = {"limit": limit}
        
        if project_id:
            params["project_id"] = project_id
        if filter_string:
            params["filter"] = filter_string
            
        return await self._make_request("GET", "tasks", params=params)

    async def complete_task(self, task_id: str) -> Dict:
        """Mark a task as completed"""
        return await self._make_request("POST", f"tasks/{task_id}/close")