from validations.users import BaseUser

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