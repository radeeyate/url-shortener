from pymongo import MongoClient
import secrets
from typing import Optional, Union
from fastapi import FastAPI, Request, Form, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

client = MongoClient("your connection string")
db = client["url-shortener"]
urls = db["urls"]
 
app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/add")
def add(request: Request, url: str = Form(), custom: Union[str, None] = Form(default=None)):
    if urls.find_one({"endpoint": custom}) is not None:
        return templates.TemplateResponse("index.html", {"request": request, "uhoh": "taken"})
    else:
        if not custom is None:
            urls.insert_one({"url": url, "endpoint": custom})
            return {"url": f"/{custom}"}
        else:
            endpoint = secrets.token_hex(6)
            urls.insert_one({"url": url, "endpoint": endpoint})
            return {"url": f"/{endpoint}"}

@app.get("/{url}")
def url(request: Request, url: str):
    query = urls.find_one({"endpoint": url}, projection = {"url": 1})
    if not query is None:
        return RedirectResponse(query["url"])
    else:
        return templates.TemplateResponse("404.html", {"request": request})
