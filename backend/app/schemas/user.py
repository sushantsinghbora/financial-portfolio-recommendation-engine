from pydantic import BaseModel, EmailStr


# Used while registering a user
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


# Used while returning user information
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True


# Used while returning JWT token
class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str