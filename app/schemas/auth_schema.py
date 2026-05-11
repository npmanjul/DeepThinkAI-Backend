from typing import Optional
from pydantic import BaseModel, EmailStr, Field,model_validator

class SignupSchema(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=50
    )
    email: EmailStr
    password: str = Field(
        min_length=6,
        max_length=20
    )
    phone: str = Field(
        min_length=10,
        max_length=10
    )


class LoginSchema(BaseModel):
    email: Optional[EmailStr]=None
    phone: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=10
    )
    password: str = Field(
        min_length=6,
        max_length=20
    )
    @model_validator(mode="after")
    def validate_email_or_phone(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone is required")
        return self


class GoogleAuthSchema(BaseModel):
    credential:str

class OTPSchema(BaseModel):
    email:str

class OTPVerifySchema(BaseModel):
    email:str
    otp:str


class ResetPasswordSchema(BaseModel):
    new_password:str
