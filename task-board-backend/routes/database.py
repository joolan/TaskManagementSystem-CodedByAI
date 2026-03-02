from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
import shutil
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import tempfile
from pydantic import BaseModel

from db import get_db
from auth import get_admin_user, get_current_user, check_permission

router = APIRouter()


def require_permission(permission_code: str):
    """Create a dependency that requires a specific permission"""
    async def dependency(
        current_user: str = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> str:
        return await check_permission(permission_code, current_user, db)
    return dependency


DATABASE_PATH = "task_board.db"
BACKUP_DIR = "backups"

BEIJING_TZ = timezone(timedelta(hours=8))


class DatabaseValidationResult(BaseModel):
    is_valid: bool
    missing_tables: List[str] = []
    missing_columns: Dict[str, List[str]] = {}
    extra_tables: List[str] = []


class BackupResponse(BaseModel):
    success: bool
    message: str
    backup_file: Optional[str] = None


class RestoreResponse(BaseModel):
    success: bool
    message: str
    validation_result: Optional[DatabaseValidationResult] = None


def ensure_backup_dir():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)


def get_table_columns(db: Session, table_name: str) -> List[str]:
    result = db.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
    return [row[1] for row in result]


def get_all_tables(db: Session) -> List[str]:
    result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")).fetchall()
    return [row[0] for row in result]


def validate_database_structure(backup_db_path: str, current_db: Session) -> DatabaseValidationResult:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    backup_engine = create_engine(f"sqlite:///{backup_db_path}")
    BackupSession = sessionmaker(bind=backup_engine)
    backup_db = BackupSession()
    
    try:
        current_tables = get_all_tables(current_db)
        backup_tables = get_all_tables(backup_db)
        
        result = DatabaseValidationResult(is_valid=True)
        
        for table in current_tables:
            if table not in backup_tables:
                result.is_valid = False
                result.missing_tables.append(table)
            else:
                current_columns = get_table_columns(current_db, table)
                backup_columns = get_table_columns(backup_db, table)
                
                missing_cols = [col for col in current_columns if col not in backup_columns]
                if missing_cols:
                    result.is_valid = False
                    result.missing_columns[table] = missing_cols
        
        return result
    finally:
        backup_db.close()
        backup_engine.dispose()


def backup_database() -> BackupResponse:
    ensure_backup_dir()
    
    if not os.path.exists(DATABASE_PATH):
        return BackupResponse(
            success=False,
            message="数据库文件不存在"
        )
    
    try:
        now = datetime.now(BEIJING_TZ)
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        db_name = os.path.splitext(os.path.basename(DATABASE_PATH))[0]
        backup_filename = f"{db_name}_backup_{timestamp}.db"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        shutil.copy2(DATABASE_PATH, backup_path)
        
        return BackupResponse(
            success=True,
            message="数据库备份成功",
            backup_file=backup_filename
        )
    except Exception as e:
        return BackupResponse(
            success=False,
            message=f"数据库备份失败: {str(e)}"
        )


@router.post("/database/backup", response_model=BackupResponse)
async def create_database_backup(
    current_user: str = Depends(require_permission("database:backup")),
    db: Session = Depends(get_db)
):
    try:
        result = backup_database()
        return result
    except Exception as e:
        return BackupResponse(
            success=False,
            message=f"数据库备份失败: {str(e)}"
        )


@router.post("/database/restore", response_model=RestoreResponse)
async def restore_database(
    file: UploadFile = File(...),
    current_user: str = Depends(require_permission("database:restore")),
    db: Session = Depends(get_db)
):
    ensure_backup_dir()
    
    if not file.filename.endswith('.db'):
        return RestoreResponse(
            success=False,
            message="只支持.db格式的数据库文件"
        )
    
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name
        
        validation_result = validate_database_structure(temp_file_path, db)
        
        if not validation_result.is_valid:
            error_msg = "数据库结构校验失败"
            if validation_result.missing_tables:
                error_msg += f"\n缺失的表: {', '.join(validation_result.missing_tables)}"
            if validation_result.missing_columns:
                for table, cols in validation_result.missing_columns.items():
                    error_msg += f"\n表 {table} 缺失的字段: {', '.join(cols)}"
            
            return RestoreResponse(
                success=False,
                message=error_msg,
                validation_result=validation_result
            )
        
        backup_result = backup_database()
        if not backup_result.success:
            return RestoreResponse(
                success=False,
                message=f"还原前备份失败: {backup_result.message}"
            )
        
        shutil.copy2(temp_file_path, DATABASE_PATH)
        
        return RestoreResponse(
            success=True,
            message=f"数据库还原成功，已自动备份当前数据库为 {backup_result.backup_file}",
            validation_result=validation_result
        )
    except Exception as e:
        return RestoreResponse(
            success=False,
            message=f"数据库还原失败: {str(e)}"
        )
    finally:
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass


@router.get("/database/backups")
async def list_backups(
    current_user: str = Depends(require_permission("database:list_backups")),
    db: Session = Depends(get_db)
):
    ensure_backup_dir()
    
    try:
        backups = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.endswith('.db'):
                filepath = os.path.join(BACKUP_DIR, filename)
                stat = os.stat(filepath)
                backups.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
        
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        return backups
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取备份列表失败: {str(e)}"
        )


@router.delete("/database/backups/{filename}")
async def delete_backup(
    filename: str,
    current_user: str = Depends(require_permission("database:delete_backup")),
    db: Session = Depends(get_db)
):
    ensure_backup_dir()
    
    filepath = os.path.join(BACKUP_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="备份文件不存在"
        )
    
    if not filename.endswith('.db'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持.db格式的数据库文件"
        )
    
    try:
        os.remove(filepath)
        return {"detail": "备份文件删除成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除备份文件失败: {str(e)}"
        )


@router.get("/database/validate")
async def validate_backup_file(
    file: UploadFile = File(...),
    current_user: str = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.db'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持.db格式的数据库文件"
        )
    
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as temp_file:
            temp_file.write(await file.read())
            temp_file_path = temp_file.name
        
        validation_result = validate_database_structure(temp_file_path, db)
        
        return validation_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"校验失败: {str(e)}"
        )
    finally:
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass
