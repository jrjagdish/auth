from pydantic import BaseModel


# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str

class UserInDB(UserCreate):
    hashed_password: str

class TodoCreate(BaseModel):
    text: str

class TodoOut(TodoCreate):
    id: str
    completed: bool

class Token(BaseModel):
    access_token: str
    token_type: str



    