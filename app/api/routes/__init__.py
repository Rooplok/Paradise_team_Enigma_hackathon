from .health import router as health_router
from .tickets import router as tickets_router
from .kb import router as kb_router
from .email import router as email_router
from .export import router as export_router

all_routers = [
    health_router,
    tickets_router,
    kb_router,
    email_router,
    export_router,
]