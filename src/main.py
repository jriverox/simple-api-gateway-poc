import re
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import httpx
import jwt
from jwt import PyJWKClient
import logging
from typing import List, Optional

from config.models import RouteConfig
from config.settings import get_settings
from handlers import HANDLER_MAPPING

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar configuración
settings = get_settings(settings_path="settings.yaml")

app = FastAPI(title=settings.app_name)
security = HTTPBearer()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allowed_origins,
    allow_credentials=settings.cors.allow_credentials,
    allow_methods=settings.cors.allowed_methods,
    allow_headers=settings.cors.allowed_headers,
)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        jwks_client = PyJWKClient(f"https://{settings.auth.auth0_domain}/.well-known/jwks.json")
        signing_key = jwks_client.get_signing_key_from_jwt(credentials.credentials)
        
        payload = jwt.decode(
            credentials.credentials,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.auth.auth0_audience,
            issuer=f"https://{settings.auth.auth0_domain}/"
        )
        
        return payload
    except Exception as e:
        logger.error(f"Token validation error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status code: {response.status_code}")
    return response

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway_handler(request: Request, path: str) -> dict:
    try:
        # Normalizar el path
        normalized_path = f"/{path}" if not path.startswith("/") else path
        
        # Buscar la ruta correspondiente
        route_config = find_matching_route(
            routes=settings.routes,
            request_method=request.method,
            normalized_path=normalized_path
        )
        
        if not route_config:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Extraer los parámetros de la ruta
        path_params = extract_path_params(route_config.path, normalized_path)
        logger.info(f"Extracted path parameters: {path_params}")
        
        # Construir la URL de destino
        target_url = route_config.target_url
        logger.info(f"Original target_url: {target_url}")
        
        # Reemplazar los parámetros en la URL
        for param_name, param_value in path_params.items():
            if param_value is not None:
                placeholder = f"{{{param_name}}}"
                target_url = target_url.replace(placeholder, str(param_value))
                
        logger.info(f"Final target_url: {target_url}")
        
        # Realizar la petición al backend
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers={
                    "Content-Type": "application/json"
                }
            )
            
            logger.info(f"Backend response status: {response.status_code}")
            if response.status_code >= 400:
                logger.error(f"Backend error response: {response.text}")
                
            return response.json()
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
def _paths_match(route_path: str, request_path: str) -> bool:
    """
    Compara si una ruta de request coincide con una ruta configurada.
    Maneja parámetros en la ruta.
    """
    # Normalizar paths
    route_parts = route_path.strip("/").split("/")
    request_parts = request_path.strip("/").split("/")
    
    if len(route_parts) != len(request_parts):
        return False
    
    for route_part, request_part in zip(route_parts, request_parts):
        # Si es un parámetro (está entre llaves), siempre coincide
        if route_part.startswith("{") and route_part.endswith("}"):
            continue
        # Si no es parámetro, debe coincidir exactamente
        if route_part != request_part:
            return False
    
    return True

def find_matching_route(routes: List[RouteConfig], request_method: str, normalized_path: str) -> Optional[RouteConfig]:
    """
    Busca una ruta configurada que coincida con el método y path de la petición.
    
    Args:
        routes: Lista de configuraciones de rutas disponibles
        request_method: Método HTTP de la petición (GET, POST, etc.)
        normalized_path: Path de la petición normalizado
        
    Returns:
        RouteConfig si encuentra coincidencia, None si no encuentra
    """
    for route in routes:
        method_matches = route.method == request_method
        path_matches = _paths_match(route.path, normalized_path)
        
        if method_matches and path_matches:
            return route
            
    return None

def extract_path_params(route_path: str, actual_path: str) -> dict:
    """
    Extrae los parámetros de la URL basándose en el patrón de la ruta.
    
    Por ejemplo:
    route_path: "/api/pet/{pet_id}"
    actual_path: "/api/pet/1"
    return: {"pet_id": "1"}
    """
    # Convertir el patrón de ruta a una expresión regular
    pattern = re.sub(r'{([^}]+)}', '(?P<\\1>[^/]+)', route_path)
    pattern = f'^{pattern}$'
    
    # Intentar hacer match con la ruta actual
    match = re.match(pattern, actual_path)
    if match:
        return match.groupdict()
    return {}