from typing import List, Optional
from pydantic import BaseModel

class RouteConfig(BaseModel):
    service_name: str
    method: str
    path: str
    target_url: Optional[str] = None
    handler: Optional[str] = None
    required_scopes: List[str] = []

class AuthConfig(BaseModel):
    auth0_domain: str
    auth0_audience: str
    backend_api_key: str

class CorsConfig(BaseModel):
    allowed_origins: List[str]
    allowed_methods: List[str]
    allowed_headers: List[str]
    allow_credentials: bool = True

class Settings(BaseModel):
    app_name: str
    environment: str
    auth: AuthConfig
    cors: CorsConfig
    routes: List[RouteConfig]