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

class ServiceAction(BaseUser):
    service: str

class AddPasswordRequest(ServiceAction):
    service_password: str
    
class RetrievePassword(ServiceAction):
    pass

class UpdatePassword(ServiceAction):
    new_service_password: str

class DeletePassword(ServiceAction):
    pass 

class ViewServices(ServiceAction):
    pass