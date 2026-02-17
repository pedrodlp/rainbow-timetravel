from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.routes import router as v1_router
from app.api.v2.routes import router as v2_router
from app.core.db import init_db


# This is async because FastAPI's lifespan expects an async context manager, even though our initialization is synchronous.
# This allows us to perform any necessary setup before the application starts handling requests.
@asynccontextmanager
async def lifespan(_: FastAPI):
    # Initialize the database before the application starts
    init_db()
    yield


app = FastAPI(title="timetravel", version="0.1.0", lifespan=lifespan)
# Include API routers for different versions of the API
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")
