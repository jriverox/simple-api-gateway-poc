from typing import Dict, Type
from .base import BaseHandler
from .custom_handlers import UserDashboardHandler, BatchUpdateHandler

HANDLER_MAPPING: Dict[str, Type[BaseHandler]] = {
    "custom_handlers.user_dashboard": UserDashboardHandler,
    "custom_handlers.batch_update": BatchUpdateHandler
}