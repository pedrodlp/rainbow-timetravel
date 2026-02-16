from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routes import router as v1_router
from app.core.db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="timetravel", version="0.1.0", lifespan=lifespan)
app.include_router(v1_router, prefix="/api/v1")
