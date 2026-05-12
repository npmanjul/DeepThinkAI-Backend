from sqlalchemy.orm import Session

from fastapi import APIRouter,Depends, Request,status,Response
from app.controller import auth
from app.schemas.auth_schema import ResetPasswordSchema, SignupSchema,LoginSchema,GoogleAuthSchema,OTPSchema,OTPVerifySchema
from app.core.database import get_db


auth_router = APIRouter(prefix="/test",tags=["Test"])

@auth_router.get("/",status_code=status.HTTP_201_CREATED)
async def test_endpoint():
    return {"message": "Test endpoint is working!"}