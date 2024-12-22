from abc import ABC, abstractmethod
from fastapi import Request
from typing import Any, Dict
import httpx

class BaseHandler(ABC):
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        self.backend_api_key = settings["auth"]["backend_api_key"]
    
    def get_headers(self) -> Dict[str, str]:
        return {
            "X-API-Key": self.backend_api_key,
            "Content-Type": "application/json"
        }
    
    @abstractmethod
    async def handle(self, request: Request) -> Dict[str, Any]:
        pass