from pydantic import BaseModel, Field


class LoginBody(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class RegisterBody(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
