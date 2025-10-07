# main.py
from fastapi import FastAPI
from app.api.api import api_router 

app = FastAPI(
    title="FastAPI Modular Project",
    description="Example of FastAPI Modulization",
    version="1.0.0",
)

# Integrate all API 
app.include_router(api_router, prefix="/api/v1")

# Server Excution Command: uvicorn main:app --reload