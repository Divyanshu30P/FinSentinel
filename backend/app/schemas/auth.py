from pydantic import BaseModel
from typing import Optional

class UserRegister(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    username: str
    is_demo: bool

class UserOut(BaseModel):
    id: str
    email: str
    username: str
    is_demo: bool
