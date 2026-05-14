from fastapi import FastAPI
from typing import Optional

app = FastAPI()

user_list = [
   "Asim",
   "Saud",
   "Atiya"
]


@app.get('/')
async def read_root():
    return {'message': 'Bismillah!!'}

@app.get('/greet/{username}')
async def greet(username:str):
    return {"message": f"Hello {username}"}

@app.get('/greet/')
async def greet(username:Optional[str]='User'):
    return {"message": f"Hello {username}"}

@app.get('/search')
async def search_for_user(username:str):
        if username in user_list:
            return {"message": f"Users details fetched for {username}"}
        else:
            return {"message": "User not found."}