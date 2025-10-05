import json, os

def create_json(name:str, data: dict):
    try:
        with open(f"..data/{name}.json", 'w', encoding='utf-8') as new_file:
            json.dump(data, new_file, indent=4, ensure_ascii=False)
        return True, None
    except Exception as e:
        return False, str(e)
    
def get_json(name:str):
    try: 
        with open(f"..data/{name}.json", 'w', encoding='utf-8') as get_file:
            get_data = json.load(get_file)

        return True, get_data
    except Exception as e:
        return False, str(e)

def update_json(name: str, type: str, data: dict):
    try: 
        with open(f"..data/{name}.json", 'w', encoding='utf-8') as update_file:
            update_data = json.load(update_file)
            
        update_data["type"] = type if type is not None else update_data["type"]
        update_data["data"] = data if data is not None else update_data["data"]
        
        with open(f"..data/{name}.json", 'w', encoding='utf-8') as update_file:
            json.dump(update_data, update_file, indent=4, ensure_ascii=False)
        
        return True, None
    except Exception as e:
        return False, str(e)
    
def delete_json(name: str):
    try: 
        if os.path.exists(f"..data/name{name}"):
            os.remove(f"..data/name{name}")
            return True, None
        else:
            return False, "File is not Found"
    except Exception as e:
        return False, str(e)