from fastapi import FastAPI
from backend.models.anomaly import Base
from backend.database import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PULSE API")

from backend.api.outbreak import router as outbreak_router
app.include_router(outbreak_router)