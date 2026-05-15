from fastapi import FastAPI, Header
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

user_list = [
   "Asim",
   "Saud",
   "Atiya"
]
users = []
class UserSchema(BaseModel):
     username:str
     email:str


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
    
@app.post('/create_user')
async def create_user(user_data:UserSchema):
    new_user = {
                'username' : user_data.username,
                'email' : user_data.email
             }
    users.append(new_user)
    return {'message': 'Users created successfully.','user':new_user}

@app.get('/get_headers')
async def get_all_request_headers(
     user_agent: Optional[str] = Header(None),
     accept_encoding: Optional[str] = Header(None),
     referer: Optional[str] = Header(None),
     connection: Optional[str] = Header(None),
     accept_language: Optional[str] = Header(None),
     host: Optional[str] = Header(None),
):
     request_headers={}
     request_headers["user_agent"]=user_agent
     request_headers["accept_encoding"]=accept_encoding
     request_headers["referer"]=referer
     request_headers["connection"]=connection
     request_headers["accept_language"]=accept_language
     request_headers["host"]=host

     return request_headers
