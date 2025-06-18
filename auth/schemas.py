from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    fullname: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    fullname: str
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str
