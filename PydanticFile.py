from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str
    created_at: Optional[datetime] = None

class UserLogin(BaseModel):
    username: str
    password: str

class userResetPassword(BaseModel):
    username:str
    current_password:str
    new_password:str

class userDeleteRequest(BaseModel):
    username:str
    password:str
    
class addPasswordRequest(BaseModel):
    username:str
    password:str
    service:str
    service_password:str
    
class retrievePassword(BaseModel):
    username:str
    password:str
    service:str
    
class updatePassword(BaseModel):
    username:str
    password:str
    service:str
    new_service_Password:str

class deletePassword(BaseModel):
    username:str
    password:str
    service:str

class viewServices(BaseModel):
    username:str
    password:str
