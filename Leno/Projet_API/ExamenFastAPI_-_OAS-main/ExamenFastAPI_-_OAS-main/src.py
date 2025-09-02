from datetime import datetime
from typing import List, Dict
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends
import json

app = FastAPI()

security = HTTPBasic()

# Bonus - Route authentifiée
@app.get("/ping/auth", response_class=PlainTextResponse)
async def ping_auth(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "admin"
    correct_password = "123456"
    
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return "pong"

# Chargement initial des posts depuis le fichier JSON
posts_db: List[Dict] = []
try:
    with open("test_posts.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        posts_db = data if isinstance(data, list) else [data]
except (FileNotFoundError, json.JSONDecodeError):
    posts_db = []

# Q1 - Route GET /ping
@app.get("/ping", response_class=PlainTextResponse, status_code=200)
async def ping():
    return "pong"

# Q2 - Route GET /home
@app.get("/home", response_class=HTMLResponse, status_code=200)
async def home():
    welcome_home = Path("components/welcomeHome.html").read_text(encoding="utf-8")
    return HTMLResponse(content=welcome_home, status_code=200)

# Q3 - Gestion des erreurs 404
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    error_404 = Path("components/error.html").read_text(encoding="utf-8")
    return HTMLResponse(content=error_404, status_code=404)

# Modèle Pydantic pour les posts
class Post(BaseModel):
    author: str
    title: str
    content: str
    creation_datetime: datetime

# Q4 - Route POST /posts
@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_posts(new_posts: List[Post]):
    try:
        new_posts_dicts = [post.dict() for post in new_posts]
        posts_db.extend(new_posts_dicts)
        
        with open("test_posts.json", "w", encoding="utf-8") as file:
            json.dump(posts_db, file, indent=4, default=str)
        
        return posts_db
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Q5 - Route GET /posts
@app.get("/posts", status_code=200)
async def get_posts():
    return posts_db

# Q6 - Route PUT /posts (idempotente)
@app.put("/posts", status_code=200)
async def update_post(post: Post):
    try:
        post_dict = post.dict()
        updated = False
        
        for idx, p in enumerate(posts_db):
            if p["title"] == post.title:
                posts_db[idx] = post_dict
                updated = True
                break
        
        if not updated:
            posts_db.append(post_dict)
        
        with open("test_posts.json", "w", encoding="utf-8") as file:
            json.dump(posts_db, file, indent=4, default=str)
        
        return posts_db
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Erreur de validation: {str(e)}")