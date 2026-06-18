from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import HTTPException
from fastapi import status, Request, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.service import UserService
from src.auth.models import User
from src.auth.schemas import UserResponseSchema
from src.db.redis import token_in_blocklist
from src.auth.utils import decode_token, TokenExpiredError, TokenInvalidError


class TokenBearer(HTTPBearer):
    def __init__(self,  auto_error = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request:Request):
        creds:HTTPAuthorizationCredentials =  await super().__call__(request)
        token = creds.credentials

        try:
            token_data = decode_token(token)
        except TokenExpiredError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error":"Token has expired",
                    "resolution":"Please refresh your token"
                },
                headers={"WWW-Authenticate":"Bearer"}
            )
        except TokenInvalidError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error":"Token is invalid",
                    "resolution":"Please login again"
                },
                headers={"WWW-Authenticate":"Bearer"}
            )
        # ─── BLOCKLIST CHECK ─────────────────────────────
        jti = token_data.get("jti")
        if jti and await token_in_blocklist(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error":"Token has been revoked",
                    "resolution":"Please login again"
                },
                headers={"WWW-Authenticate":"Bearer"}
            )
        
        self.verify_token_data(token_data=token_data)
        return token_data
    
    def verify_token_data(self, token_data:dict)->None:
        raise NotImplementedError("Please override this method in child classes")

class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        print("========================",token_data)
        token_type = token_data.get("type") or token_data.get("token_type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid token type", 
                        "resolution": "Please provide an access token"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        
class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:  # ← "token_data"
        token_type = token_data.get("type") or token_data.get("token_type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "Invalid token type", 
                        "resolution": "Please provide a refresh token"},
                headers={"WWW-Authenticate": "Bearer"},
            )


# ─── Instance to use in routes ─────────────────────────
access_token_bearer = AccessTokenBearer()
refresh_token_bearer = RefreshTokenBearer()

# ─── Full user dependency ──────────────────────────────
async def get_current_user(
        token_data:dict =Depends(access_token_bearer),
        session:AsyncSession=Depends(get_session)
)->User:
    user_uid = token_data.get("sub")
    if not user_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_service = UserService()
    user = await user_service.get_user_by_uid(user_uid, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # user_data = {
    #     "username": user.username,
    #     "email": user.email,
    #     "uid": str(user.uid),
    #     "first_name": user.first_name,
    #     "last_name": user.last_name,
    #     "is_verified": user.is_verified,
    #     "created_at": user.created_at.isoformat(),
    #     "updated_at": user.updated_at.isoformat()

    # }

    return UserResponseSchema.model_validate(user)