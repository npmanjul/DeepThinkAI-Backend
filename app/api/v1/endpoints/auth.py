from sqlalchemy.orm import Session

from fastapi import APIRouter,Depends, Request,status,Response
from app.controller import auth
from app.schemas.auth_schema import ResetPasswordSchema, SignupSchema,LoginSchema,GoogleAuthSchema,OTPSchema,OTPVerifySchema
from app.core.database import get_db


auth_router = APIRouter(prefix="/auth",tags=["Auth"])

@auth_router.post("/signup",status_code=status.HTTP_201_CREATED)
async def signup(user_data:SignupSchema, response: Response,db: Session = Depends(get_db)):
    return await auth.signup(user_data,db,response)

@auth_router.post("/login",status_code=status.HTTP_200_OK)
async def login(user_data:LoginSchema,response: Response, db: Session = Depends(get_db) ):
    return await auth.login(user_data,db,response)

@auth_router.post("/google-auth",status_code=status.HTTP_200_OK)
async def google_auth(user_data:GoogleAuthSchema,response: Response, db: Session = Depends(get_db) ):
    return await auth.google_auth(user_data,db,response)

@auth_router.post("/get-otp",status_code=status.HTTP_200_OK)
async def get_otp(user_email:OTPSchema, db: Session = Depends(get_db)):
    return await auth.generate_otp(user_email,db)

@auth_router.post("/verify-otp",status_code=status.HTTP_200_OK)
async def verify_otp(otp_detail:OTPVerifySchema,response:Response, db: Session = Depends(get_db)):
    return await auth.verify_otp(otp_detail,response, db)

@auth_router.post("/reset-password",status_code=status.HTTP_200_OK)
async def reset_password(resetpassword_data:ResetPasswordSchema,request: Request ,db: Session = Depends(get_db)):
    return await auth.reset_password(resetpassword_data, db,request)

@auth_router.post("/logout",status_code=status.HTTP_200_OK)
async def logout(response: Response):
    return await auth.logout(response)