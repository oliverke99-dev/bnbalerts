from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
import logging
from bson import ObjectId

from app.models.user import (
    UserCreate, UserResponse, UserInDB,
    LoginRequest, LoginResponse, SignupResponse,
    VerifyPhoneRequest, VerifyPhoneResponse,
    ForgotPasswordRequest, ForgotPasswordResponse,
    ResetPasswordRequest, ResetPasswordResponse
)
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.otp import generate_otp
from app.integrations.twilio_client import send_sms
from app.db.mongodb import get_database
from app.core.constants import OTP_EXPIRY_MINUTES

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInDB:
    """
    Dependency to get current authenticated user from JWT token.
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Convert string ID to ObjectId for MongoDB query
    try:
        user_object_id = ObjectId(user_id)
    except Exception as e:
        logger.error(f"Invalid user ID format in token: {user_id}, error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    # Get user from database
    db = get_database()
    user_doc = await db.users.find_one({"_id": user_object_id})
    
    if user_doc is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return UserInDB(**user_doc)


@router.post("/signup", response_model=SignupResponse)
async def signup(user_data: UserCreate):
    """
    Register a new user with email, password, and phone.
    Sends OTP via SMS for phone verification.
    """
    db = get_database()
    
    # Check if email already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate OTP
    otp = generate_otp()
    otp_expiry = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    
    # Hash password
    password_hash = hash_password(user_data.password)
    
    # Create user document
    user_doc = {
        "email": user_data.email,
        "passwordHash": password_hash,
        "phone": user_data.phone,
        "phoneVerified": False,
        "phoneOtp": otp,
        "phoneOtpExpiry": otp_expiry,
        "name": None,
        "tier": "free",
        "smsEnabled": True,
        "emailEnabled": False,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    # Insert user into database
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = str(result.inserted_id)
    
    # Send OTP via SMS
    sms_message = f"Your BnBAlerts verification code is: {otp}"
    send_sms(user_data.phone, sms_message)
    
    logger.info(f"User registered: {user_data.email}, OTP sent to {user_data.phone}")
    
    # Return user response
    user_response = UserResponse(
        id=str(result.inserted_id),
        email=user_data.email,
        phone=user_data.phone,
        phoneVerified=False,
        tier="free",
        smsEnabled=True,
        emailEnabled=False
    )
    
    return SignupResponse(
        user=user_response,
        message="OTP sent to phone"
    )


@router.post("/verify-phone", response_model=VerifyPhoneResponse)
async def verify_phone(verify_data: VerifyPhoneRequest):
    """
    Verify phone number with OTP code.
    Returns JWT token upon successful verification.
    """
    logger.info(f"verify_phone called with userId: {verify_data.userId}")
    db = get_database()
    
    # Convert string ID to ObjectId for MongoDB query
    try:
        user_object_id = ObjectId(verify_data.userId)
    except Exception as e:
        logger.error(f"Invalid user ID format: {verify_data.userId}, error: {e}")
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    # Find user by ID
    user_doc = await db.users.find_one({"_id": user_object_id})
    if not user_doc:
        logger.error(f"User not found for ID: {verify_data.userId}")
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if OTP matches and hasn't expired
    if user_doc.get("phoneOtp") != verify_data.code:
        raise HTTPException(status_code=400, detail="Invalid OTP code")
    
    if user_doc.get("phoneOtpExpiry") and user_doc["phoneOtpExpiry"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP code has expired")
    
    # Update user: mark phone as verified and clear OTP
    await db.users.update_one(
        {"_id": user_object_id},
        {
            "$set": {
                "phoneVerified": True,
                "phoneOtp": None,
                "phoneOtpExpiry": None,
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    # Generate JWT token (use string ID for JWT)
    token = create_access_token({"sub": verify_data.userId})
    
    logger.info(f"Phone verified for user: {verify_data.userId}")
    
    return VerifyPhoneResponse(success=True, token=token)


@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """
    Authenticate user with email and password.
    Returns JWT token if credentials are valid and phone is verified.
    """
    db = get_database()
    
    # Find user by email
    user_doc = await db.users.find_one({"email": login_data.email})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(login_data.password, user_doc["passwordHash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if phone is verified
    if not user_doc.get("phoneVerified", False):
        raise HTTPException(status_code=403, detail="Phone not verified. Please verify your phone number.")
    
    # Generate JWT token
    token = create_access_token({"sub": str(user_doc["_id"])})
    
    # Create user response
    user_response = UserResponse(
        id=str(user_doc["_id"]),
        email=user_doc["email"],
        phone=user_doc["phone"],
        phoneVerified=user_doc["phoneVerified"],
        name=user_doc.get("name"),
        tier=user_doc.get("tier", "free"),
        smsEnabled=user_doc.get("smsEnabled", True),
        emailEnabled=user_doc.get("emailEnabled", False)
    )
    
    logger.info(f"User logged in: {login_data.email}")
    
    return LoginResponse(token=token, user=user_response)


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user (token invalidation handled client-side).
    """
    # In a stateless JWT system, logout is primarily handled client-side
    # by removing the token from storage. This endpoint exists for consistency
    # and could be extended to implement token blacklisting if needed.
    
    logger.info("User logged out")
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: UserInDB = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    """
    return UserResponse(
        id=str(current_user.id) if current_user.id else "",
        email=current_user.email,
        phone=current_user.phone,
        phoneVerified=current_user.phoneVerified,
        name=current_user.name,
        tier=current_user.tier,
        smsEnabled=current_user.smsEnabled,
        emailEnabled=current_user.emailEnabled
    )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Request password reset. Sends OTP code to user's email.
    """
    db = get_database()
    
    # Find user by email
    user_doc = await db.users.find_one({"email": request.email})
    if not user_doc:
        # Don't reveal if email exists or not for security
        return ForgotPasswordResponse(
            message="If an account exists with this email, a reset code has been sent.",
            email=request.email
        )
    
    # Generate OTP for password reset
    otp = generate_otp()
    otp_expiry = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    
    # Store OTP in user document
    await db.users.update_one(
        {"_id": user_doc["_id"]},
        {
            "$set": {
                "passwordResetOtp": otp,
                "passwordResetOtpExpiry": otp_expiry,
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    # Send OTP via SMS to user's phone
    sms_message = f"Your BnBAlerts password reset code is: {otp}. This code expires in {OTP_EXPIRY_MINUTES} minutes."
    send_sms(user_doc["phone"], sms_message)
    
    logger.info(f"Password reset OTP sent to phone for user: {request.email}")
    
    return ForgotPasswordResponse(
        message="If an account exists with this email, a reset code has been sent.",
        email=request.email
    )


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(request: ResetPasswordRequest):
    """
    Reset password using OTP code sent to email.
    """
    db = get_database()
    
    # Find user by email
    user_doc = await db.users.find_one({"email": request.email})
    if not user_doc:
        raise HTTPException(status_code=400, detail="Invalid reset code or email")
    
    # Check if OTP matches and hasn't expired
    if user_doc.get("passwordResetOtp") != request.code:
        raise HTTPException(status_code=400, detail="Invalid reset code")
    
    if user_doc.get("passwordResetOtpExpiry") and user_doc["passwordResetOtpExpiry"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset code has expired")
    
    # Hash new password
    new_password_hash = hash_password(request.newPassword)
    
    # Update password and clear reset OTP
    await db.users.update_one(
        {"_id": user_doc["_id"]},
        {
            "$set": {
                "passwordHash": new_password_hash,
                "passwordResetOtp": None,
                "passwordResetOtpExpiry": None,
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    logger.info(f"Password reset successful for user: {request.email}")
    
    return ResetPasswordResponse(
        success=True,
        message="Password has been reset successfully"
    )