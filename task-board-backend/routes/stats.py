from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from db import get_db, User, Task, Status, TaskFollow, Release, ReleaseFollow, Requirement, TaskHour, Defect
from schemas import TaskStatusStats, UserWorkloadStats, ProjectProgressStats
from auth import get_current_active_user

router = APIRouter()


@router.get("/task-status", response_model=list[TaskStatusStats])
async def get_task_status_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get task status statistics"""
    # Get status counts
    status_counts = db.query(
        Status.id,
        Status.name,
        Status.color,
        func.count(Task.id).label('count')
    ).outerjoin(
        Task, Task.status_id == Status.id
    ).group_by(
        Status.id, Status.name, Status.color
    ).order_by(
        Status.order_index
    ).all()
    
    # Convert to schema
    return [
        TaskStatusStats(
            status_name=sc.name,
            count=sc.count or 0,
            color=sc.color
        )
        for sc in status_counts
    ]


@router.get("/user-workload", response_model=list[UserWorkloadStats])
async def get_user_workload_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user workload statistics"""
    # Get user workload
    user_workload = db.query(
        User.id,
        User.username,
        User.name,
        func.count(Task.id).label('task_count'),
        func.coalesce(func.sum(Task.estimated_hours), 0).label('estimated_hours'),
        func.coalesce(func.sum(Task.actual_hours), 0).label('actual_hours')
    ).outerjoin(
        Task, Task.assignee_id == User.id
    ).group_by(
        User.id, User.username, User.name
    ).all()
    
    # Convert to schema
    return [
        UserWorkloadStats(
            user_id=uw.id,
            username=uw.username,
            name=uw.name,
            task_count=uw.task_count or 0,
            estimated_hours=float(uw.estimated_hours),
            actual_hours=float(uw.actual_hours)
        )
        for uw in user_workload
    ]


@router.get("/project-progress", response_model=ProjectProgressStats)
async def get_project_progress_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get project progress statistics"""
    # Get total tasks
    total_tasks = db.query(func.count(Task.id)).scalar() or 0
    
    # Get completed tasks (status: 已完成)
    completed_status = db.query(Status).filter(Status.name == "已完成").first()
    completed_tasks = 0
    if completed_status:
        completed_tasks = db.query(func.count(Task.id)).filter(
            Task.status_id == completed_status.id
        ).scalar() or 0
    
    # Calculate completion rate
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Get overdue tasks
    overdue_tasks = db.query(func.count(Task.id)).filter(
        Task.due_date < date.today(),
        Task.status_id != completed_status.id if completed_status else True
    ).scalar() or 0
    
    # Return stats
    return ProjectProgressStats(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        completion_rate=round(completion_rate, 2),
        overdue_tasks=overdue_tasks
    )


@router.get("/dashboard")
async def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard metrics for current user"""
    # Get uncompleted statuses (待办、进行中、已暂停)
    uncompleted_statuses = db.query(Status).filter(
        Status.name.in_(["待办", "进行中", "已暂停"])
    ).all()
    uncompleted_status_ids = [s.id for s in uncompleted_statuses]
    
    # Get completed status
    completed_status = db.query(Status).filter(Status.name == "已完成").first()
    completed_status_id = completed_status.id if completed_status else None
    
    # 1. 我负责的未完成任务
    my_assigned_tasks = db.query(func.count(Task.id)).filter(
        (
            (Task.assignee_id == current_user.id) |
            (Task.assignees.any(User.id == current_user.id))
        ),
        Task.status_id.in_(uncompleted_status_ids)
    ).scalar() or 0
    
    # 2. 我关注的未完成任务
    my_followed_tasks = db.query(func.count(Task.id)).join(
        TaskFollow, Task.id == TaskFollow.task_id
    ).filter(
        TaskFollow.user_id == current_user.id,
        Task.status_id.in_(uncompleted_status_ids)
    ).scalar() or 0
    
    # 3. 我关注的未发版本
    my_followed_releases = db.query(func.count(Release.id)).join(
        ReleaseFollow, Release.id == ReleaseFollow.release_id
    ).filter(
        ReleaseFollow.user_id == current_user.id,
        Release.status.in_(["计划中", "延期中"])
    ).scalar() or 0
    
    # 4. 我创建的待处理需求
    my_requirements = db.query(func.count(Requirement.id)).filter(
        Requirement.created_by == current_user.id,
        Requirement.status.in_(["草稿", "待评审", "已确认"])
    ).scalar() or 0
    
    # 5. 我负责的未完成缺陷
    my_assigned_defects = db.query(func.count(Defect.id)).filter(
        Defect.assignee_id == current_user.id,
        Defect.status.in_(["草稿", "未解决"])
    ).scalar() or 0
    
    # Return dashboard metrics
    return {
        "myAssignedTasksCount": my_assigned_tasks,
        "myFollowedTasksCount": my_followed_tasks,
        "myFollowedReleasesCount": my_followed_releases,
        "myRequirementsCount": my_requirements,
        "myAssignedDefectsCount": my_assigned_defects
    }


@router.get("/overview")
async def get_overview_stats(
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get overview statistics with optional date range filter"""
    from datetime import datetime
    
    # Parse date range if provided
    start_datetime = None
    end_datetime = None
    
    if start_date:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date:
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Base queries
    task_query = db.query(Task)
    release_query = db.query(Release)
    requirement_query = db.query(Requirement)
    defect_query = db.query(Defect)
    task_hour_query = db.query(TaskHour).filter(TaskHour.user_id == current_user.id)
    
    # Apply date filters if provided
    if start_datetime:
        task_query = task_query.filter(Task.created_at >= start_datetime)
        release_query = release_query.filter(Release.created_at >= start_datetime)
        requirement_query = requirement_query.filter(Requirement.created_at >= start_datetime)
        defect_query = defect_query.filter(Defect.created_at >= start_datetime)
        task_hour_query = task_hour_query.filter(TaskHour.created_at >= start_datetime)
    if end_datetime:
        task_query = task_query.filter(Task.created_at <= end_datetime)
        release_query = release_query.filter(Release.created_at <= end_datetime)
        requirement_query = requirement_query.filter(Requirement.created_at <= end_datetime)
        defect_query = defect_query.filter(Defect.created_at <= end_datetime)
        task_hour_query = task_hour_query.filter(TaskHour.created_at <= end_datetime)
    
    # Get uncompleted statuses (待办、进行中、已暂停)
    uncompleted_statuses = db.query(Status).filter(
        Status.name.in_(["待办", "进行中", "已暂停"])
    ).all()
    uncompleted_status_ids = [s.id for s in uncompleted_statuses]
    
    # Get completed status
    completed_status = db.query(Status).filter(Status.name == "已完成").first()
    completed_status_id = completed_status.id if completed_status else None
    
    # Task statistics
    task_uncompleted = task_query.filter(
        Task.status_id.in_(uncompleted_status_ids)
    ).count()
    
    task_completed = task_query.filter(
        Task.status_id == completed_status_id
    ).count() if completed_status_id else 0
    
    task_other = task_query.filter(
        ~Task.status_id.in_(uncompleted_status_ids + ([completed_status_id] if completed_status_id else []))
    ).count()
    
    # Release statistics
    release_uncompleted = release_query.filter(
        Release.status.in_(["计划中", "延期中"])
    ).count()
    
    release_completed = release_query.filter(
        Release.status == "已发版"
    ).count()
    
    release_other = release_query.filter(
        ~Release.status.in_(["计划中", "延期中", "已发版"])
    ).count()
    
    # Requirement statistics
    requirement_uncompleted = requirement_query.filter(
        Requirement.status.in_(["草稿", "待评审", "已确认"])
    ).count()
    
    requirement_completed = requirement_query.filter(
        Requirement.status == "已转任务"
    ).count()
    
    requirement_other = requirement_query.filter(
        ~Requirement.status.in_(["草稿", "待评审", "已确认", "已转任务"])
    ).count()
    
    # Defect statistics
    defect_uncompleted = defect_query.filter(
        Defect.status.in_(["草稿", "未解决"])
    ).count()
    
    defect_completed = defect_query.filter(
        Defect.status == "已解决"
    ).count()
    
    defect_other = defect_query.filter(
        ~Defect.status.in_( ["草稿", "未解决", "已解决"] )
    ).count()
    
    # My hours statistics
    my_hours_completed = task_hour_query.with_entities(
        func.coalesce(func.sum(TaskHour.hours), 0.0)
    ).scalar() or 0.0
    my_hours_uncompleted = 0
    my_hours_other = 0
    
    # Return overview stats
    return {
        "task": {
            "uncompleted": task_uncompleted,
            "completed": task_completed,
            "other": task_other
        },
        "release": {
            "uncompleted": release_uncompleted,
            "completed": release_completed,
            "other": release_other
        },
        "requirement": {
            "uncompleted": requirement_uncompleted,
            "completed": requirement_completed,
            "other": requirement_other
        },
        "defect": {
            "uncompleted": defect_uncompleted,
            "completed": defect_completed,
            "other": defect_other
        },
        "my_hours": {
            "uncompleted": my_hours_uncompleted,
            "completed": float(my_hours_completed),
            "other": my_hours_other
        }
    }
