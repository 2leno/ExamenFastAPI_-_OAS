from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.get("/ping", response_class=PlainTextResponse, status_code=200)
async def ping():
    return "pong"