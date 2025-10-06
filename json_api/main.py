from app import control_json
from fastapi import FastAPI
from pydantic import BaseModel

# FastAPI Instance
app = FastAPI()

class Item(BaseModel):
    name: str
    data: dict 

@app.get('/item/{name}')
def get_item(name: str):
    valid, data = control_json.get_json(name=name)
    if valid == True:
        return {"message": "Get Item Sucessfully", "data": data}
    else:
        return {"error": f"Get Item Failure: {data}"}

@app.post('/item')
def post_item(item: Item):

    valid, data = control_json.create_json(name=item.name, data=item.data)
    if valid == True:
        return {"message": "Create Item Sucessfully"}
    else:
        return {"error": f"Create Item Failure: {data}"}
    
@app.put('/item/{name}')
def put_item(name: str, data: dict):

    valid, data = control_json.update_json(name=name, data=data)
    if valid == True:
        return {"message": "Update Item Sucessfully"}
    else:
        return {"error": f"Update Item Failure: {data}"}
    
@app.delete('/item/{name}')
def delete_item(name: str):
    valid, data = control_json.delete_json(name=name)
    if valid == True:
        return {"message": "Delete Item Sucessfully"}
    else:
        return {"error": f"Delete Item Failure: {data}"}