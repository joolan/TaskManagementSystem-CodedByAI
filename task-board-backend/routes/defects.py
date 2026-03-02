from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import pandas as pd
import io

from db import get_db, User, Defect, Release, Message, UserMessage
from auth import get_current_user, get_current_active_user, check_permission

router = APIRouter()


def require_permission(permission_code: str):
    """Create a dependency that requires a specific permission"""
    async def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        return await check_permission(permission_code, current_user, db)
    return dependency


# Schemas
class DefectBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "草稿"
    release_id: Optional[int] = None
    assignee_id: Optional[int] = None


class DefectCreate(DefectBase):
    pass


class DefectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    release_id: Optional[int] = None
    assignee_id: Optional[int] = None


class DefectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    release_id: Optional[int]
    created_by: int
    assignee_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DefectWithDetails(DefectResponse):
    creator_name: Optional[str] = None
    assignee_name: Optional[str] = None
    release_title: Optional[str] = None
    
    class Config:
        from_attributes = True


class DefectListResponse(BaseModel):
    items: List[DefectWithDetails]
    total: int
    page: int
    page_size: int


# Helper function to get defect with details
def get_defect_with_details(db: Session, defect: Defect) -> DefectWithDetails:
    """Get defect with related user and release information"""
    defect_dict = {
        "id": defect.id,
        "title": defect.title,
        "description": defect.description,
        "status": defect.status,
        "release_id": defect.release_id,
        "created_by": defect.created_by,
        "assignee_id": defect.assignee_id,
        "created_at": defect.created_at,
        "updated_at": defect.updated_at,
        "creator_name": defect.creator.name if defect.creator else None,
        "assignee_name": defect.assignee.name if defect.assignee else None,
        "release_title": defect.release.title if defect.release else None
    }
    return DefectWithDetails(**defect_dict)


def send_defect_notification(db: Session, defect: Defect, assignee_id: int, creator_id: int):
    """Send notification to defect assignee"""
    # Get assignee and creator information
    assignee = db.query(User).filter(User.id == assignee_id).first()
    creator = db.query(User).filter(User.id == creator_id).first()
    
    if not assignee:
        return
    
    # Create message with redirect path
    message = Message(
        message_type="defect_message",
        title=f"新缺陷分配",
        content=f"您被分配了一个新的缺陷：{defect.title}",
        redirect_path=f"/defect/{defect.id}",
        created_by=creator_id
    )
    db.add(message)
    db.flush()  # Get message ID without committing
    
    # Create user message
    user_message = UserMessage(
        user_id=assignee_id,
        message_id=message.id
    )
    db.add(user_message)
    
    # Commit changes
    db.commit()


# Endpoints
@router.get("", response_model=DefectListResponse)
async def get_defects(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    release_id: Optional[int] = Query(None),
    assignee_id: Optional[int] = Query(None),
    created_by: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get defects with pagination and filtering"""
    query = db.query(Defect)
    
    # Apply filters
    if status:
        # 处理前端传递的状态参数，支持单个状态或多个状态
        status_values = []
        if isinstance(status, list):
            status_values = status
        else:
            # 检查是否是逗号分隔的多个状态
            if ',' in status:
                status_values = status.split(',')
            else:
                status_values = [status]
        print(f"Status values to filter: {status_values}")
        query = query.filter(Defect.status.in_(status_values))
    if release_id:
        query = query.filter(Defect.release_id == release_id)
    if assignee_id:
        query = query.filter(Defect.assignee_id == assignee_id)
    if created_by:
        query = query.filter(Defect.created_by == created_by)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    defects = query.order_by(Defect.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    # Get defects with details
    defect_list = []
    for defect in defects:
        defect_list.append(get_defect_with_details(db, defect))
    
    return DefectListResponse(
        items=defect_list,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/export")
async def export_defects(
    status: Optional[str] = Query(None, description="Filter by status"),
    release_id: Optional[int] = Query(None, description="Filter by release ID"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    created_by: Optional[int] = Query(None, description="Filter by creator ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("defect:export"))
):
    """Export defects with optional filters to Excel file"""
    query = db.query(Defect).options(
        joinedload(Defect.creator),
        joinedload(Defect.assignee),
        joinedload(Defect.release)
    )

    # Apply filters
    if status:
        # Split comma-separated string into list of statuses
        statuses = [s.strip() for s in status.split(',')]
        query = query.filter(Defect.status.in_(statuses))
    if release_id:
        query = query.filter(Defect.release_id == release_id)
    if assignee_id:
        query = query.filter(Defect.assignee_id == assignee_id)
    if created_by:
        query = query.filter(Defect.created_by == created_by)

    # Get all defects without pagination
    defects = query.all()

    # Prepare data for export
    data = []
    for defect in defects:
        # Prepare row data
        row = {
            "缺陷ID": defect.id,
            "缺陷标题": defect.title,
            "缺陷描述": defect.description,
            "缺陷状态": defect.status,
            "缺陷来源版本": defect.release.title if defect.release else "无",
            "负责人": defect.assignee.name if defect.assignee else "未分配",
            "创建人": defect.creator.name if defect.creator else "",
            "创建时间": defect.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "更新时间": defect.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        data.append(row)

    # Create DataFrame
    df = pd.DataFrame(data)

    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='缺陷列表', index=False)
    output.seek(0)

    # Return as streaming response
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=defects_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )


@router.get("/{defect_id}", response_model=DefectWithDetails)
async def get_defect(
    defect_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get defect by ID"""
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not defect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Defect not found"
        )
    return get_defect_with_details(db, defect)


@router.post("", response_model=DefectWithDetails)
async def create_defect(
    defect: DefectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("defect:create"))
):
    """Create a new defect"""
    # Validate release_id if provided
    if defect.release_id:
        release = db.query(Release).filter(Release.id == defect.release_id).first()
        if not release:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Release not found"
            )
    
    # Validate assignee_id if provided
    if defect.assignee_id:
        assignee = db.query(User).filter(User.id == defect.assignee_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee not found"
            )
    
    db_defect = Defect(
        title=defect.title,
        description=defect.description,
        status=defect.status,
        release_id=defect.release_id,
        assignee_id=defect.assignee_id,
        created_by=current_user.id
    )
    db.add(db_defect)
    db.commit()
    db.refresh(db_defect)
    
    # Send notification if assignee is set
    if defect.assignee_id:
        send_defect_notification(db, db_defect, defect.assignee_id, current_user.id)
    
    return get_defect_with_details(db, db_defect)


@router.put("/{defect_id}", response_model=DefectWithDetails)
async def update_defect(
    defect_id: int,
    defect: DefectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("defect:update"))
):
    """Update defect"""
    db_defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not db_defect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Defect not found"
        )
    
    # Validate release_id if provided
    if defect.release_id is not None:
        release = db.query(Release).filter(Release.id == defect.release_id).first()
        if not release:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Release not found"
            )
        db_defect.release_id = defect.release_id
    
    # Validate assignee_id if provided
    old_assignee_id = db_defect.assignee_id
    if defect.assignee_id is not None:
        assignee = db.query(User).filter(User.id == defect.assignee_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assignee not found"
            )
        db_defect.assignee_id = defect.assignee_id
    
    # Update other fields
    if defect.title is not None:
        db_defect.title = defect.title
    if defect.description is not None:
        db_defect.description = defect.description
    if defect.status is not None:
        db_defect.status = defect.status
    
    db_defect.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_defect)
    
    # Send notification if assignee has changed
    if old_assignee_id != defect.assignee_id and defect.assignee_id:
        send_defect_notification(db, db_defect, defect.assignee_id, current_user.id)
    
    return get_defect_with_details(db, db_defect)


@router.delete("/{defect_id}")
async def delete_defect(
    defect_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("defect:delete"))
):
    """Delete defect"""
    db_defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if not db_defect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Defect not found"
        )
    db.delete(db_defect)
    db.commit()
    return {"message": "Defect deleted successfully"}
