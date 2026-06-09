from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.routes import router
from db.database import create_db_pool

@asynccontextmanager
async def lifespan(app: FastAPI):

    await create_db_pool()

    yield

app = FastAPI(
    title="Retail GenAI SQL Assistant",
    lifespan=lifespan
)

app.include_router(router)