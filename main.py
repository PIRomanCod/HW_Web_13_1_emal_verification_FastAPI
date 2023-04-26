import time

import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from src.database.db import get_db
from src.routes import contacts, search, auth, users

app = FastAPI()

origins = [
    "http://localhost:3000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware('http')
async def custom_middleware(request: Request, call_next):
    """
    The custom_middleware function is a middleware function that adds the time it took to process the request in seconds as a header called 'performance'

    :param request: Request: Access the request object
    :param call_next: Call the next middleware in the chain
    :return: A response object that has a performance header
    :doc-author: Trelent
    """
    start_time = time.time()
    response = await call_next(request)
    during = time.time() - start_time
    response.headers['performance'] = str(during)
    return response


@app.middleware("http")
async def errors_handling(request: Request, call_next):
    """
    The errors_handling function is a middleware that catches any exception raised by the application.
    It returns an error response with status code 500 and a JSON body containing the reason for the error.

    :param request: Request: Get the request object
    :param call_next: Call the next handler in the chain
    :return: A json response with a status code of 500 and the error message
    :doc-author: Trelent
    """
    try:
        return await call_next(request)
    except Exception as exc:
        return JSONResponse(status_code=500, content={'reason': str(exc)})


templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse, description="Main Page")
async def root(request: Request):
    """
    The root function is the entry point for the application.
    It returns a TemplateResponse object, which renders an HTML template using Jinja2.
    The template is located in templates/index.html and uses data from the request object to render itself.

    :param request: Request: Get the request object
    :return: The index
    :doc-author: Trelent
    """
    return templates.TemplateResponse('index.html', {"request": request, "title": "Contact Manager"})


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks the health of the database.
    It does this by making a request to the database and checking if it returns any results.
    If there are no results, then we know something is wrong with our connection.

    :param db: Session: Get the database session from the dependency
    :return: A dictionary with a message key
    :doc-author: Trelent
    """
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


app.include_router(auth.router)
app.include_router(contacts.router)
app.include_router(search.search)
app.include_router(users.router)


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are needed by your app, such as database connections or external APIs.
    - In this case its initialized Redis as connects limiter

    :return: A coroutine, so we need to use asyncio
    :doc-author: Trelent
    """
    from src.conf.config import settings
    r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0, encoding="utf-8",
                          decode_responses=True)
    await FastAPILimiter.init(r)


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
