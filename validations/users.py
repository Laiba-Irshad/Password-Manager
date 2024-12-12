
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BaseUser(BaseModel):
    username: str
    password: str
    
class UserCreate(BaseUser):
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

class UserLogin(BaseUser):
    pass

class UserResetPassword(BaseUser):
    new_password: str

class UserDeleteRequest(BaseUser):
    pass