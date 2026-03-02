from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from db import get_db, User, UserSession, Permission

# Load environment variables
load_dotenv()

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

# Password hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    # Ensure password length is within bcrypt limit (72 bytes)
    if len(password) > 72:
        password = password[:72]
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # Check if session is still active
    session = db.query(UserSession).filter(
        UserSession.token == token,
        UserSession.is_active == 1
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update session activity
    update_session_activity(db, token)
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    return current_user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current admin user"""
    if current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_pm_or_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current PM or admin user"""
    # 由于已移除role字段，此函数暂时只检查admin用户
    # 权限检查将通过权限切片进行
    if current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def check_permission(permission_code: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    """Check if user has required permission
    
    Args:
        permission_code: Permission code to check. If None or empty string, only check token validity.
        current_user: Current user from token.
        db: Database session.
    
    Returns:
        User object if permission check passes.
    
    Raises:
        HTTPException: If user doesn't have the required permission.
    """
    # Admin user has all permissions
    if current_user.username == "admin":
        return current_user
    
    # If permission_code is None or empty string, only check token validity (already done by get_current_user)
    if permission_code is None or permission_code == "":
        return current_user
    
    # Check if user has the required permission
    # First, check if user has the permission directly (extra permissions)
    from db import user_permissions
    user_permission = db.query(Permission).join(
        user_permissions
    ).filter(
        Permission.code == permission_code,
        user_permissions.c.user_id == current_user.id
    ).first()
    
    if user_permission:
        return current_user
    
    # Second, check if user has the permission through roles
    from db import role_permissions, user_roles
    for role in current_user.roles:
        role_permission = db.query(Permission).join(
            role_permissions
        ).filter(
            Permission.code == permission_code,
            role_permissions.c.role_id == role.id
        ).first()
        
        if role_permission:
            return current_user
    
    # User doesn't have the required permission
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Permission denied. Required permission: {permission_code}"
    )


def create_user_session(db: Session, user_id: int, token: str, ip_address: str = None, user_agent: str = None) -> UserSession:
    """Create a new user session"""
    session = UserSession(
        user_id=user_id,
        token=token,
        ip_address=ip_address,
        user_agent=user_agent,
        login_at=datetime.utcnow(),
        last_activity_at=datetime.utcnow(),
        is_active=1
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_max_sessions_per_user(db: Session) -> int:
    """Get maximum sessions per user from system settings"""
    from db import SystemSetting
    setting = db.query(SystemSetting).filter(SystemSetting.key == "max_sessions_per_user").first()
    if setting:
        try:
            return int(setting.value)
        except ValueError:
            return 2  # Default value
    return 2  # Default value


def manage_user_sessions(db: Session, user_id: int, new_token: str, ip_address: str = None, user_agent: str = None) -> UserSession:
    """Manage user sessions, enforce max sessions limit"""
    max_sessions = get_max_sessions_per_user(db)
    
    # Get active sessions for this user
    active_sessions = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_active == 1
    ).order_by(UserSession.login_at).all()
    
    # If we have reached the limit, deactivate the oldest sessions
    if len(active_sessions) >= max_sessions:
        sessions_to_deactivate = len(active_sessions) - max_sessions + 1
        for i in range(sessions_to_deactivate):
            active_sessions[i].is_active = 0
        db.commit()
    
    # Create new session
    return create_user_session(db, user_id, new_token, ip_address, user_agent)


def update_session_activity(db: Session, token: str) -> None:
    """Update session last activity time"""
    session = db.query(UserSession).filter(
        UserSession.token == token,
        UserSession.is_active == 1
    ).first()
    if session:
        session.last_activity_at = datetime.utcnow()
        db.commit()


def get_user_sessions(db: Session, user_id: int) -> list:
    """Get all active sessions for a user"""
    # First, get all active sessions
    sessions = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_active == 1
    ).all()
    
    # Check for expired sessions
    active_sessions = []
    for session in sessions:
        # Calculate expiration time (last activity time + token expire time)
        expire_time = session.last_activity_at + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        if datetime.utcnow() < expire_time:
            # Session is still active
            active_sessions.append(session)
        else:
            # Session has expired, mark as inactive
            session.is_active = 0
    
    # Commit changes for expired sessions
    if len(sessions) != len(active_sessions):
        db.commit()
    
    # Order by login time desc
    active_sessions.sort(key=lambda x: x.login_at, reverse=True)
    
    return active_sessions


def revoke_session(db: Session, session_id: int) -> bool:
    """Revoke a user session"""
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if session:
        session.is_active = 0
        db.commit()
        return True
    return False
