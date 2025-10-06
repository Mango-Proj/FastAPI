import json, os
DATA_PATH = "/Users/shannon/Documents/Programming/mango_proj/fastapi/json_api/data"
def create_json(name:str, data: dict):
    try:
        with open(f"{DATA_PATH}/{name}.json", 'w', encoding='utf-8') as new_file:
            json.dump(data, new_file, indent=4, ensure_ascii=False)
        return True, None
    except Exception as e:
        return False, str(e)
    
def get_json(name:str):
    try: 
        with open(f"{DATA_PATH}/{name}.json", 'r', encoding='utf-8') as get_file:
            get_data = json.load(get_file)

        print(get_data)
        return True, get_data
    except Exception as e:
        print(e)
        return False, str(e)

def update_json(name: str, data: dict):
    try: 
        with open(f"{DATA_PATH}/{name}.json", 'r', encoding='utf-8') as update_file:
            update_data = json.load(update_file)
            
        update_data = data
        
        with open(f"{DATA_PATH}/{name}.json", 'w', encoding='utf-8') as update_file:
            json.dump(update_data, update_file, indent=4, ensure_ascii=False)
        
        return True, None
    except Exception as e:
        return False, str(e)
    
def delete_json(name: str):
    try: 
        if os.path.exists(f"{DATA_PATH}/{name}.json"):
            os.remove(f"{DATA_PATH}/{name}.json")
            return True, None
        else:
            return False, "File is not Found"
    except Exception as e:
        return False, str(e)