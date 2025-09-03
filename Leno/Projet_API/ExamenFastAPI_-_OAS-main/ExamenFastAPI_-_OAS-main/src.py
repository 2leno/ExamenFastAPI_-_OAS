from datetime import datetime
from typing import Optional, List
from pathlib import Path
import yaml
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse, PlainTextResponse
from pydantic import BaseModel

app = FastAPI()

PHONES_FILE = "phones.yml"

def load_phones_from_yaml():
    try:
        with open(PHONES_FILE, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, yaml.YAMLError):
        return []

def save_posts_to_yaml(posts):
    try:
        with open(PHONES_FILE, "w", encoding="utf-8") as file:
            yaml.dump(posts, file, allow_unicode=True, default_flow_style=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'écriture YAML: {str(e)}")

phones_db = load_phones_from_yaml   

class phones(BaseModel):
    id: int
    brand: str
    model: str
    
@app.get("/health", response_class=PlainTextResponse, status_code=200)
async def health():
    return "ok"

@app.get("/phones", response_model=List[phones], status_code=200)
async def users():
    mock_phones = [
        {"id": 1, "brand": "Samsung", "model": "Galaxy A21s"},
        {"id": 2, "brand": "Apple", "model": "Iphone 12 Pro Max"}
    ],
    return mock_phones

@app.post("/phones", status_code=201)
async def create_posts(new_posts: Optional[List[phones]] = None):
    try:
        if new_posts is None:
            return phones_db 
        
        new_phones_dicts = [post.dict() for post in new_posts]
        phones_db.extend(new_phones_dicts)
        save_posts_to_yaml(phones_db)
        return phones_db
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/phones", status_code=200)
async def get_posts():
    return phones_db

@app.put("/phones", status_code=200)
async def update_post(post: phones):
    try:
        post_dict = post.dict()
        updated = False
        
        for idx, p in enumerate(phones_db):
            if p.get("id") == post.id:
                phones_db[idx] = post_dict
                updated = False
                break
        
        if not updated:
            phones_db.append(post_dict)
        
        save_posts_to_yaml(phones_db)
        return phones_db
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Erreur de validation: {str(e)}")
