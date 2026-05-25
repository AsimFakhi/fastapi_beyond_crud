from fastapi import APIRouter, Depends, status, Response
from src.auth.schemas import UserCreateSchema, UserResponseSchema,UserLoginSchema, TokenUserData
from src.auth.service import UserService
from src.db.main import get_session
from src.auth.utils import create_access_token, create_refresh_token, verify_password, generate_password_hash
from src.auth.dependencies import refresh_token_bearer, access_token_bearer
from src.db.redis import add_jti_to_blocklist
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from datetime import timedelta, timezone, datetime
from src.config import CONF

auth_router = APIRouter()
user_service = UserService()


@auth_router.post("/signup", 
                  response_model=UserResponseSchema, 
                  status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data:UserCreateSchema, session:AsyncSession =Depends(get_session)):
    email=user_data.email
    user_exist = await user_service.user_exists(email, session)
    if user_exist:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with email already exists."
        )
    new_user = await user_service.create_user(user_data, session)
    return new_user

@auth_router.post("/login")
async def login_users(
    login_data: UserLoginSchema,
    response: Response,
    session: AsyncSession = Depends(get_session)
):
    email = login_data.email
    password = login_data.password
    user = await user_service.get_user_by_email(email, session)
    # print("User Found ==========>>> ", user)
    if user is not None:
        password_valid = verify_password(password, user.password_hash)
    else:
        dummy_hash = generate_password_hash("dummy")
        verify_password(password, dummy_hash)
        password_valid = False
    if not password_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid email or password.")
    user_data = {
        "uid": str(user.uid),
        "email": user.email,
        "username": user.username,
    }
    # print(user_data)
    access_token = create_access_token(user_data=user_data)
    refresh_token = create_refresh_token(user_data=user_data)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=CONF.REFRESH_TOKEN_EXPIRY_DAYS
    )

    return JSONResponse(
        content={
            "message":"Login Successful",
            "access_token": access_token,
            "authorization_paste": f"Bearer {access_token}",
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": CONF.ACCESS_TOKEN_EXPIRY_MINUTES*60,
            "user": {"email":user.email, "uid":str(user.uid)}
        }
    )

# ─── REFRESH ENDPOINT ──────────────────────────────────
@auth_router.post("/refresh")
async def refresh_access_token(token_data:dict=Depends(refresh_token_bearer)):
    """
    Exchange a valid refresh token for a new access token.
    Client must send refresh token in Authorization header 
    or (better) in HTTP-only cookie.
    """

    user_data = token_data.get("user",{})
    # print("==================================",user_data)
    #Issue new access token
    new_access_token = create_access_token(user_data=user_data) 

    return JSONResponse(
        content={
            "message": "Token refreshed successfully",
            "access_token":new_access_token,
            "token_type": "bearer",
            "expires_in": CONF.ACCESS_TOKEN_EXPIRY_MINUTES*60,
            "user": {"email":user_data.get("email"), "uid":user_data.get("uid")}
        }
    )

# ─── LOGOUT (Optional but recommended) ─────────────────
@auth_router.post("/logout")
async def logout(
    response: Response,
    token_data: dict = Depends(access_token_bearer)
):
    """
    Revoke the current access token by adding its JTI to the blocklist.
    Also clear the refresh token cookie.
    """
    jti = token_data.get("jti")
    exp = token_data.get("exp")

    if jti:
        # Calculate remaining token lifetime for Redis expiry
        if exp:
            now = datetime.now(timezone.utc).timestamp()
            ttl = int(exp - now)
            if ttl > 0:
                await add_jti_to_blocklist(jti, expiry=ttl)
        else:
            # Fallback: block for default access token duration
            await add_jti_to_blocklist(jti, expiry=CONF.ACCESS_TOKEN_EXPIRY_MINUTES * 60)

    # Clear refresh token cookie
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="strict",
    )

    return {"message": "Logged out successfully. Token revoked."}