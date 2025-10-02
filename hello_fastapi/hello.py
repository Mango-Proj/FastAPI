from fastapi import FastAPI
from pydantic import BaseModel

# FastAPI Instance
app = FastAPI()

class Item(BaseModel):
    type: str
    data: dict 

# Get Method of "/"
@app.get("/")
def read_root():
    return {"message": "Hello Fast API"}

@app.post("/")
def process_root(request_item: Item):
    
    return {"message": f"Post method: {request_item.type}, {request_item.data}"}
