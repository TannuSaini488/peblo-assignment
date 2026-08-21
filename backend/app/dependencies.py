from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.storage.base import StorageBackend
from app.storage.local import LocalStorageBackend
from app.storage.r2 import R2StorageBackend

security = HTTPBearer()

def get_storage() -> StorageBackend:
    if settings.storage_backend == "r2":
        return R2StorageBackend(
            account_id=settings.storage_r2_account_id,
            access_key=settings.storage_r2_access_key_id,
            secret_key=settings.storage_r2_secret_access_key,
            bucket=settings.storage_r2_bucket
        )
    return LocalStorageBackend(base_path=settings.storage_local_path)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user

def require_role(required_roles: list[str]):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of roles: {', '.join(required_roles)}"
            )
        return current_user
    return role_checker

# Helper dependencies
def get_editor_user(user: User = Depends(require_role(["editor", "admin"]))) -> User:
    return user

def get_admin_user(user: User = Depends(require_role(["admin"]))) -> User:
    return user
