from sqlalchemy.orm import Session
from fastapi import HTTPException ,Request,Response
from app.schemas.auth_schema import ResetPasswordSchema, SignupSchema,LoginSchema,GoogleAuthSchema,OTPSchema,OTPVerifySchema
from app.models.model import OTP, User
from sqlalchemy import or_
from app.utils.hash import hash_password,verify_password
from app.utils.jwt import create_access_token
from app.utils.googleAuth import verify_google_token
import os
from app.utils.email import send_email
from app.utils.mail_templates import otp_template
from app.utils.generateOTP import generate_six_digit_otp

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

async def signup(
    user_data: SignupSchema,
    db: Session,
    response:Response
):
    user=db.query(User).filter(or_(
        User.email == user_data.email,
        User.phone == user_data.phone
    )).first()

    if user:
        raise HTTPException(status_code=400, detail="Email or phone already exists")
    
    hashed_password=hash_password(user_data.password)
    
    create_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
        phone=user_data.phone
    )

    db.add(create_user)
    db.commit()
    db.refresh(create_user)

    return {
        "message": "Signup Successful"
    }


async def login(
    user_data: LoginSchema,
    db: Session,
    response:Response
):
    filters = []
    if user_data.email:
        filters.append(User.email == user_data.email)
    if user_data.phone:
        filters.append(User.phone == user_data.phone)

    user = db.query(User).filter(or_(*filters)).first()

    if not user:
        raise HTTPException(status_code=400,detail="Invalid credentials")
    
    if user.is_google_auth:
        raise HTTPException(status_code=400,detail="Please login with Google")
    
    if not verify_password(user_data.password,user.password):
        raise HTTPException(status_code=400,detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.id})
    # Cookie security settings: use Secure+SameSite=None in production (HTTPS).
    secure_cookie = os.getenv("ENV", "development") == "production"
    samesite_policy = "none" if secure_cookie else "lax"

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=secure_cookie,
        samesite=samesite_policy,
        max_age=60 * 60,
        expires=60 * 60,
    )
        
    return {
        "message": "Login Successful",
    }


async def google_auth(
    user_data:GoogleAuthSchema, 
    db: Session,
    response: Response
):
    user_detail=verify_google_token(user_data.credential)
    email = user_detail.get("email")
    name = user_detail.get("name") or "Google User"

    if not email:
        raise HTTPException(status_code=400, detail="Google account email not found")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(
            name=name,
            email=email,
            is_google_auth=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": user.id})
    
    secure_cookie = os.getenv("ENV", "development") == "production"
    samesite_policy = "none" if secure_cookie else "lax"

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=secure_cookie,
        samesite=samesite_policy,
        max_age=60 * 60,
        expires=60 * 60,
    )

    return {
        "message": "Google Authentication Successful",
    }


async def generate_otp(
    user_email:OTPSchema,
    db: Session
):
    user = db.query(User).filter(User.email == user_email.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Email does not exist")

    existing_otp = db.query(OTP).filter(OTP.email == user_email.email).first()

    if existing_otp:
        db.delete(existing_otp)
        db.commit()

    otp=generate_six_digit_otp()

    new_otp = OTP(
        email=user_email.email,
        otp=otp
    )
    db.add(new_otp)
    db.commit()
    db.refresh(new_otp)

    sent = send_email(
        to_email=user_email.email,
        subject="Verify Your Email Address",
        html_content=otp_template(otp),
    )

    if not sent:
        raise HTTPException(status_code=500, detail="Failed to send OTP email")
    
    return {
        "message": "OTP sent to email"
    }


async def verify_otp(
    otp_detail: OTPVerifySchema,
    response: Response,
    db: Session,
):
    user_otp = (
        db.query(OTP)
        .filter(OTP.email == otp_detail.email)
        .first()
    )

    if not user_otp:
        raise HTTPException(
            status_code=400,
            detail="Email does not exist"
        )

    if user_otp.otp != otp_detail.otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    user = db.query(User).filter(User.email == otp_detail.email).first()
    if not user:
        raise HTTPException(
            status_code=400,
            detail="User not found for this email"
        )

    user.is_verified = True
    access_token = create_access_token(data={"sub": user.id})

    secure_cookie = os.getenv("ENV", "development") == "production"
    samesite_policy = "none" if secure_cookie else "lax"

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=secure_cookie,
        samesite=samesite_policy,
        max_age=60 * 60,
        expires=60 * 60,
    )

    db.delete(user_otp)
    db.commit()

    return {
        "message": "OTP Verified Successfully",
    }


async def reset_password(
    resetpassword_data:ResetPasswordSchema,
    db: Session,
    request: Request
):
    user_id = request.state.user.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    hashed_password = hash_password(resetpassword_data.new_password)
    user.password = hashed_password
    db.commit()

    return {
        "message": "Password reset successful"
    }


async def logout(response: Response):
    secure_cookie = os.getenv("ENV", "development") == "production"
    samesite_policy = "none" if secure_cookie else "lax"

    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=secure_cookie,
        samesite=samesite_policy,
    )

    return {
        "message": "Logout successful"
    }