from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db import get_db, Memo
from schemas import MemoCreate, MemoUpdate, Memo as MemoSchema, MemoWithDetails
from auth import get_current_user, check_permission
from schemas import User

router = APIRouter(tags=["memos"])


def require_permission(permission_code: str):
    """Create a dependency that requires a specific permission"""
    async def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        return await check_permission(permission_code, current_user, db)
    return dependency


@router.get("", response_model=List[MemoSchema])
async def get_my_memos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的备忘录列表"""
    memos = db.query(Memo).filter(Memo.created_by == current_user.id).all()
    return memos


@router.post("", response_model=MemoSchema)
async def create_memo(
    memo: MemoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("memo:create"))
):
    """创建新的备忘录"""
    # 创建备忘录
    db_memo = Memo(
        name=memo.name,
        content=memo.content,
        created_by=current_user.id
    )
    db.add(db_memo)
    db.commit()
    db.refresh(db_memo)
    return db_memo


@router.get("/{memo_id}", response_model=MemoSchema)
async def get_memo(
    memo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取备忘录详情"""
    # 查找备忘录
    memo = db.query(Memo).filter(Memo.id == memo_id).first()
    if not memo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="备忘录不存在"
        )
    
    # 检查权限，只能查看自己的备忘录
    if memo.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此备忘录"
        )
    
    return memo


@router.put("/{memo_id}", response_model=MemoSchema)
async def update_memo(
    memo_id: int,
    memo_update: MemoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("memo:update"))
):
    """更新备忘录"""
    # 查找备忘录
    memo = db.query(Memo).filter(Memo.id == memo_id).first()
    if not memo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="备忘录不存在"
        )
    
    # 检查权限，只能更新自己的备忘录
    if memo.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权更新此备忘录"
        )
    
    # 更新备忘录
    if memo_update.name is not None:
        memo.name = memo_update.name
    if memo_update.content is not None:
        memo.content = memo_update.content
    
    db.commit()
    db.refresh(memo)
    return memo


@router.delete("/{memo_id}")
async def delete_memo(
    memo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("memo:delete"))
):
    """删除备忘录"""
    # 查找备忘录
    memo = db.query(Memo).filter(Memo.id == memo_id).first()
    if not memo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="备忘录不存在"
        )
    
    # 检查权限，只能删除自己的备忘录
    if memo.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此备忘录"
        )
    
    # 删除备忘录
    db.delete(memo)
    db.commit()
    return {"detail": "备忘录删除成功"}