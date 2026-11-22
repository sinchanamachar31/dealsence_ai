from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.sim_routes import router as sim_router
from backend.api.internal_bridge import router as internal_bridge_router
from backend.api.enterprise_routes import router as enterprise_router
from backend.database.core_db import CoreBase, core_engine
from backend.database.sim_db import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    CoreBase.metadata.create_all(bind=core_engine)
    yield


app = FastAPI(title="DealSense AI Simulation API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/static",
    StaticFiles(directory=str(Path(__file__).resolve().parent / "static")),
    name="static",
)

app.include_router(sim_router)
app.include_router(internal_bridge_router)
app.include_router(enterprise_router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "DealSense AI Simulation Backend"}
