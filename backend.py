import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import starlette.status as status
import hashlib
import sqlite3
import requests

def valid_url(url):
    try:
        requests.get(url)
        return True
    except Exception:
        return False


def init_database():
    conn = sqlite3.connect('data')
    cursor = conn.cursor()

    try:
        query = "CREATE TABLE data (ID CHARACTER(20) PRIMARY KEY, URL TEXT);"
        cursor.execute(query)
    except Exception as e:
        print(e)

    cursor.close()
    conn.close()


app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_database()


@app.get("/shortener/")
async def shortener(url: str):
    if not valid_url(url):
        return {'error': 'Invalid URL'}
    hash_object = hashlib.md5(url.encode('utf-8')).hexdigest()[:8]

    conn = sqlite3.connect('data')
    cursor = conn.cursor()

    query = f"SELECT URL FROM data WHERE ID='{hash_object}'"
    cursor.execute(query)
    res = cursor.fetchone()
    if res == None:
        query = f"INSERT INTO data VALUES (?, ?);"
        cursor.execute(query, (hash_object, url))
        conn.commit()

    cursor.close()
    conn.close()

    return {
        'url': 'http://34.122.183.83:6758/s/' + hash_object
    }

@app.get("/s/{id}")
async def redirect(id):

    conn = sqlite3.connect('data')
    cursor = conn.cursor()
    
    query = f"SELECT URL FROM data WHERE ID='{id}'"
    cursor.execute(query)
    res = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return RedirectResponse(
        res, 
        status_code=status.HTTP_302_FOUND
    )

uvicorn.run(
    app,
    host='0.0.0.0',
    port=6758,
)