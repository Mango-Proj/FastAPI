from app import control_json
from fastapi import FastAPI
from pydantic import BaseModel

# FastAPI Instance
app = FastAPI()

class Item(BaseModel):
    type: str
    data: dict 
