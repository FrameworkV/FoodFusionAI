from pydantic import BaseModel, EmailStr

class UserData(BaseModel):
    username: str
    password: str
    email: EmailStr