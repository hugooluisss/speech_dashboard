from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.controllers.health import router as health_router
from app.controllers.me import router as me_router
from app.controllers.plans import router as plans_router
from app.controllers.billing import router as billing_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    get_settings()
    yield


app = FastAPI(title="Speech Dashboard Backend", lifespan=lifespan)
app.include_router(health_router)
app.include_router(me_router)
app.include_router(plans_router)
app.include_router(billing_router)
