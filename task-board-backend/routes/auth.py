from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import Optional

from db import get_db, User, SystemSetting, LoginLog, UserSession, Role, Permission, Menu
from schemas import UserCreate, UserLogin, UserResponse, User as UserSchema, UserBasic
from auth import (
    verify_password, get_password_hash, create_access_token, get_current_user, get_current_active_user, 
    get_admin_user, ACCESS_TOKEN_EXPIRE_MINUTES, manage_user_sessions,
    get_user_sessions, revoke_session, check_permission
)

router = APIRouter()


def require_permission(permission_code: str):
    """Create a dependency that requires a specific permission"""
    async def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        return await check_permission(permission_code, current_user, db)
    return dependency


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if registration is allowed
    setting = db.query(SystemSetting).filter(SystemSetting.key == "allow_registration").first()
    if not setting or setting.value.lower() != "true":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="禁止自助注册，请联系管理员"
        )
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if name already exists
    existing_name = db.query(User).filter(User.name == user.name).first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        password=hashed_password,
        name=user.name,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    
    # Return user with token
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        name=db_user.name,
        email=db_user.email,
        created_at=db_user.created_at,
        last_login_at=db_user.last_login_at,
        token=access_token
    )


@router.post("/login", response_model=UserResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db), request: Request = None):
    """Login and get access token"""
    # Get IP address and user agent
    ip_address = request.client.host if request else "unknown"
    user_agent = request.headers.get("user-agent", "unknown") if request else "unknown"
    
    # Find user by username
    user = db.query(User).filter(User.username == user_data.username).first()
    
    # Record login attempt
    login_log = LoginLog(
        user_id=user.id if user else 0,
        ip_address=ip_address,
        user_agent=user_agent,
        status="success"
    )
    
    if not user:
        login_log.status = "failed"
        db.add(login_log)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is locked
    if user.locked_until:
        # If lock time has expired, unlock user
        if user.locked_until <= datetime.utcnow():
            user.locked_until = None
            user.failed_login_attempts = 0
            db.commit()
        else:
            # User is still locked
            login_log.status = "failed"
            db.add(login_log)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account is locked until {user.locked_until.strftime('%Y-%m-%d %H:%M:%S')}",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Verify password
    if not verify_password(user_data.password, user.password):
        # Increment failed login attempts
        user.failed_login_attempts += 1
        
        # Check if user should be locked
        if user.failed_login_attempts >= 10:
            # Lock user for 30 hours
            user.locked_until = datetime.utcnow() + timedelta(hours=30)
            login_log.status = "failed (locked)"
        else:
            login_log.status = "failed"
        
        db.add(login_log)
        db.commit()
        
        # Calculate remaining attempts
        remaining_attempts = 10 - user.failed_login_attempts
        if remaining_attempts <= 0:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account locked due to too many failed login attempts. Please contact admin.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Incorrect username or password. {remaining_attempts} attempts remaining.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    # Reset failed login attempts on successful login
    user.failed_login_attempts = 0
    user.locked_until = None
    
    # Update last login time
    user.last_login_at = datetime.utcnow()
    
    # Add login log
    db.add(login_log)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Manage user sessions (enforce max sessions limit)
    manage_user_sessions(db, user.id, access_token, ip_address, user_agent)
    
    db.commit()
    db.refresh(user)
    
    # Return user with token
    return UserResponse(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
        token=access_token
    )


@router.get("/me", response_model=UserSchema)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.get("/users")
async def get_users(
    current_user: User = Depends(require_permission("user:list")),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    username: Optional[str] = Query(None, description="Filter by username"),
    name: Optional[str] = Query(None, description="Filter by name"),
    role_id: Optional[int] = Query(None, description="Filter by role id")
):
    """Get users with pagination and filtering"""
    
    # Build query
    query = db.query(User)
    
    # Apply filters
    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))
    if name:
        query = query.filter(User.name.ilike(f"%{name}%"))
    if role_id:
        query = query.join(User.roles).filter(Role.id == role_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    users = query.offset(offset).limit(page_size).all()
    
    # Build result
    result = []
    for user in users:
        # Get active sessions
        active_sessions = get_user_sessions(db, user.id)
        session_count = len(active_sessions)
        
        # Get user roles
        user_roles = []
        for role in user.roles:
            user_roles.append({
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "status": role.status,
                "created_at": role.created_at,
                "updated_at": role.updated_at
            })
        
        user_dict = {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "roles": user_roles,
            "created_at": user.created_at,
            "last_login_at": user.last_login_at,
            "failed_login_attempts": user.failed_login_attempts,
            "locked_until": user.locked_until,
            "session_count": session_count
        }
        result.append(user_dict)
    
    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/users-basic", response_model=list[UserBasic])
async def get_users_basic(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get basic user information (id, username, name) - accessible to all logged-in users"""
    users = db.query(User).all()
    return [
        UserBasic(id=user.id, username=user.username, name=user.name)
        for user in users
    ]


@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, current_user: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Get user by ID (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user roles
    user_roles = []
    for role in user.roles:
        user_roles.append({
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "status": role.status,
            "created_at": role.created_at,
            "updated_at": role.updated_at
        })
    
    # Convert user to dict and add roles
    user_dict = {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "roles": user_roles,
        "created_at": user.created_at,
        "last_login_at": user.last_login_at,
        "failed_login_attempts": user.failed_login_attempts,
        "locked_until": user.locked_until,
        "session_count": 0  # Default session count
    }
    
    return user_dict


@router.put("/users/{user_id}", response_model=UserSchema)
async def update_user(user_id: int, user_data: UserCreate, current_user: User = Depends(require_permission("user:update")), db: Session = Depends(get_db)):
    """Update user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if username already exists (excluding current user)
    existing_user = db.query(User).filter(User.username == user_data.username, User.id != user_id).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists (excluding current user)
    existing_email = db.query(User).filter(User.email == user_data.email, User.id != user_id).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Only check if name already exists if it's changed (excluding current user)
    if user_data.name != user.name:
        existing_name = db.query(User).filter(User.name == user_data.name, User.id != user_id).first()
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Name already exists"
            )
    
    # Update user
    # user.username = user_data.username
    user.name = user_data.name
    user.email = user_data.email
    if user_data.password:
        user.password = get_password_hash(user_data.password)
    
    db.commit()
    db.refresh(user)
    
    # Get user roles
    user_roles = []
    for role in user.roles:
        user_roles.append({
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "status": role.status,
            "created_at": role.created_at,
            "updated_at": role.updated_at
        })
    
    # Convert user to dict and add roles
    user_dict = {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "email": user.email,
        "roles": user_roles,
        "created_at": user.created_at,
        "last_login_at": user.last_login_at,
        "failed_login_attempts": user.failed_login_attempts,
        "locked_until": user.locked_until,
        "session_count": 0  # Default session count
    }
    
    return user_dict


@router.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate, current_user: User = Depends(require_permission("user:create")), db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if name already exists
    existing_name = db.query(User).filter(User.name == user.name).first()
    if existing_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name already exists"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        password=hashed_password,
        name=user.name,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    
    # Return user with token
    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        name=db_user.name,
        email=db_user.email,
        created_at=db_user.created_at,
        last_login_at=db_user.last_login_at,
        token=access_token
    )


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, current_user: User = Depends(require_permission("user:delete")), db: Session = Depends(get_db)):
    """Delete user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting admin user if it's the last one
    admin_users = db.query(User).filter(User.username == "admin").count()
    if user.username == "admin" and admin_users <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the last admin user"
        )
    
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}


@router.put("/users/{user_id}/password")
async def update_user_password(user_id: int, password_data: dict, current_user: User = Depends(require_permission("user:change_password")), db: Session = Depends(get_db)):
    """Update user password"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    password = password_data.get("password")
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required"
        )
    
    user.password = get_password_hash(password)
    db.commit()
    return {"detail": "Password updated successfully"}


@router.put("/users/{user_id}/unlock")
async def unlock_user(user_id: int, current_user: User = Depends(require_permission("user:unlock")), db: Session = Depends(get_db)):
    """Unlock locked user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Unlock user
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    
    return {"detail": "User unlocked successfully"}


# UserSession endpoints


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout user and revoke current session"""
    # Get token from request
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    # Find and revoke the current session
    session = db.query(UserSession).filter(
        UserSession.token == token,
        UserSession.is_active == 1
    ).first()
    
    if session:
        session.is_active = 0
        db.commit()
    
    return {"detail": "Logged out successfully"}


@router.get("/users/{user_id}/sessions", response_model=list[dict])
async def get_user_sessions_list(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all active sessions for a user (admin only)"""
    sessions = get_user_sessions(db, user_id)
    return [
        {
            "id": session.id,
            "user_id": session.user_id,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "login_at": session.login_at,
            "last_activity_at": session.last_activity_at,
            "is_active": session.is_active
        }
        for session in sessions
    ]


@router.delete("/sessions/{session_id}")
async def revoke_user_session(
    session_id: int,
    current_user: User = Depends(require_permission("user:revoke_session")),
    db: Session = Depends(get_db)
):
    """Revoke a user session"""
    success = revoke_session(db, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return {"detail": "Session revoked successfully"}


# User role and permission endpoints


@router.post("/users/{user_id}/roles")
async def assign_roles_to_user(
    user_id: int,
    role_ids: list[int],
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Assign roles to user"""
    # Find user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent editing admin user
    if user.username == "admin":
        raise HTTPException(status_code=403, detail="Cannot edit admin user")
    
    # Clear existing roles
    user.roles.clear()
    
    # Assign new roles
    for role_id in role_ids:
        role = db.query(Role).filter(Role.id == role_id).first()
        if role:
            user.roles.append(role)
    
    db.commit()
    return {"detail": "Roles assigned successfully"}


@router.post("/users/{user_id}/permissions")
async def assign_extra_permissions_to_user(
    user_id: int,
    permission_ids: list[int],
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Assign extra permissions to user"""
    # Find user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent editing admin user
    if user.username == "admin":
        raise HTTPException(status_code=403, detail="Cannot edit admin user")
    
    # Clear existing extra permissions
    user.extra_permissions.clear()
    
    # Assign new permissions
    for permission_id in permission_ids:
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if permission:
            user.extra_permissions.append(permission)
    
    db.commit()
    return {"detail": "Extra permissions assigned successfully"}


@router.get("/users/{user_id}/roles")
async def get_user_roles(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get user roles"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return [role.id for role in user.roles]


@router.get("/users/{user_id}/permissions")
async def get_user_permissions(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get user extra permissions"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return [permission.id for permission in user.extra_permissions]


@router.get("/users/{user_id}/menus")
async def get_user_menus(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get user extra menus"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return [menu.id for menu in user.extra_menus]


@router.post("/users/{user_id}/menus")
async def assign_extra_menus_to_user(
    user_id: int,
    menu_ids: list[int],
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Assign extra menus to user"""
    # Find user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent editing admin user
    if user.username == "admin":
        raise HTTPException(status_code=403, detail="Cannot edit admin user")
    
    # Clear existing extra menus
    user.extra_menus.clear()
    
    # Assign new menus
    for menu_id in menu_ids:
        menu = db.query(Menu).filter(Menu.id == menu_id).first()
        if menu:
            user.extra_menus.append(menu)
    
    db.commit()
    return {"detail": "Extra menus assigned successfully"}


@router.get("/me/roles")
async def get_current_user_roles(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user roles"""
    # 如果用户是admin，返回所有角色
    if current_user.username == "admin":
        all_roles = db.query(Role).all()
        return [{
            "id": role.id,
            "name": role.name,
            "description": role.description
        } for role in all_roles]
    
    # 普通用户返回分配的角色
    return [{
        "id": role.id,
        "name": role.name,
        "description": role.description
    } for role in current_user.roles]


@router.get("/me/permissions")
async def get_current_user_permissions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user permissions"""
    # 如果用户是admin，返回所有权限
    if current_user.username == "admin":
        all_permissions = db.query(Permission).all()
        return [{
            "id": perm.id,
            "code": perm.code,
            "name": perm.name,
            "description": perm.description
        } for perm in all_permissions]
    
    # 普通用户获取权限
    # 从角色中获取权限
    role_permissions = set()
    for role in current_user.roles:
        for permission in role.permissions:
            role_permissions.add(permission)
    
    # 从用户额外权限中获取
    user_extra_permissions = set(current_user.extra_permissions)
    
    # 合并所有权限
    all_permissions = role_permissions.union(user_extra_permissions)
    
    return [{
        "id": perm.id,
        "code": perm.code,
        "name": perm.name,
        "description": perm.description
    } for perm in all_permissions]
