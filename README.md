# Web Gateway API

API Gateway para arquitectura de microservicios que proporciona:
- Enrutamiento de peticiones
- Control de acceso y autenticación
- Handlers personalizados para casos específicos
- Logging y monitorización

## Instalación

1. Instalar Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Clonar el repositorio e instalar dependencias:
```bash
git clone <repository-url>
cd web-gateway
poetry install
```

3. Configurar el archivo settings.yaml con tus valores

4. Ejecutar el servidor:
```bash
poetry run uvicorn web_gateway.main:app --reload
```

## Uso

El gateway soporta dos tipos de endpoints:
1. Proxy genérico: Redirección automática a servicios backend
2. Handlers personalizados: Para lógica específica y agregación de datos

### Ejemplos

Proxy genérico:
```bash
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/conversations/123
```

Handler personalizado:
```bash
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/user-dashboard/123
```

## Desarrollo
