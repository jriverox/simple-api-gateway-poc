import asyncio
from typing import Dict, Any, List
from fastapi import Request, HTTPException
from .base import BaseHandler
import httpx

class UserDashboardHandler(BaseHandler):
    async def handle(self, request: Request) -> Dict[str, Any]:
        user_id = request.path_params["user_id"]
        
        async with httpx.AsyncClient() as client:
            tasks = [
                client.get(
                    f"http://backend-core-api/users/{user_id}/profile",
                    headers=self.get_headers()
                ),
                client.get(
                    f"http://conversations-api/conversations/summary/{user_id}",
                    headers=self.get_headers()
                ),
                client.get(
                    f"http://tags-api/tags/user/{user_id}",
                    headers=self.get_headers()
                )
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        profile, conversations, tags = responses
        
        if isinstance(profile, Exception):
            raise HTTPException(status_code=500, detail="Error fetching user profile")
            
        return {
            "user": profile.json(),
            "activity": {
                "conversations": conversations.json() if not isinstance(conversations, Exception) else [],
                "tags": tags.json() if not isinstance(tags, Exception) else []
            }
        }

class BatchUpdateHandler(BaseHandler):
    async def process_update(
        self, client: httpx.AsyncClient, update: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            if update["type"] == "conversation":
                response = await client.put(
                    f"http://conversations-api/conversations/{update['id']}",
                    json=update["data"],
                    headers=self.get_headers()
                )
            elif update["type"] == "tag":
                response = await client.put(
                    f"http://tags-api/tags/{update['id']}",
                    json=update["data"],
                    headers=self.get_headers()
                )
            else:
                return {
                    "id": update["id"],
                    "success": False,
                    "error": "Unknown update type"
                }
            
            return {
                "id": update["id"],
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {
                "id": update["id"],
                "success": False,
                "error": str(e)
            }

    async def handle(self, request: Request) -> Dict[str, Any]:
        data = await request.json()
        
        if not isinstance(data, list):
            raise HTTPException(status_code=400, detail="Expected array of updates")
        
        async with httpx.AsyncClient() as client:
            tasks = [self.process_update(client, update) for update in data]
            results = await asyncio.gather(*tasks)
        
        return {
            "results": results,
            "summary": {
                "total": len(results),
                "successful": len([r for r in results if r["success"]]),
                "failed": len([r for r in results if not r["success"]])
            }
        }