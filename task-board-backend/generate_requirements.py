"""
在数据库中插入30个需求记录的脚本
"""
import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal, Requirement, RequirementTag, User

# 需求来源列表
sources = [
    "客户反馈", "市场调研", "用户访谈", "竞品分析", "内部讨论",
    "产品规划", "技术评估", "数据分析", "运营需求", "财务需求"
]

# 需求名称模板
requirement_names = [
    "用户登录功能优化", "数据导出功能", "移动端适配", "性能优化",
    "安全加固", "界面美化", "流程简化", "多语言支持",
    "第三方集成", "报表统计", "消息通知", "权限管理",
    "文件上传", "在线编辑", "版本控制", "自动化测试",
    "日志记录", "缓存优化", "数据库迁移", "API接口开发",
    "支付功能", "订单管理", "库存管理", "会员系统",
    "营销活动", "客户服务", "数据分析", "系统监控"
]

# 需求描述模板
descriptions = [
    "这是一个重要的功能需求，需要尽快实现以满足用户需求。",
    "根据用户反馈，我们需要优化这个功能以提升用户体验。",
    "这个功能是系统的核心功能之一，需要仔细设计和实现。",
    "为了提高系统的可用性，需要添加这个功能。",
    "这是一个紧急需求，需要在下一个版本中完成。",
    "根据市场调研结果，这个功能对产品的竞争力至关重要。",
    "为了满足合规要求，需要实现这个功能。",
    "这个功能可以帮助我们更好地了解用户行为和需求。",
    "为了提高系统的安全性，需要添加这个功能。",
    "这个功能可以大大提高用户的工作效率。"
]

# 需求状态列表
statuses = ["草稿", "待评审", "已确认", "已作废"]

# 需求优先级列表
priorities = ["高", "中", "低"]

def generate_requirements():
    """生成30个需求记录"""
    db = SessionLocal()
    
    try:
        # 获取或创建需求标签
        tags = db.query(RequirementTag).all()
        if not tags:
            # 如果没有标签，创建一些默认标签
            default_tags = [
                RequirementTag(name="功能优化", color="#3b82f6"),
                RequirementTag(name="性能优化", color="#10b981"),
                RequirementTag(name="安全加固", color="#ef4444"),
                RequirementTag(name="用户体验", color="#f59e0b"),
                RequirementTag(name="数据分析", color="#8b5cf6")
            ]
            db.add_all(default_tags)
            db.commit()
            db.refresh_all(default_tags)
            tags = default_tags
        
        # 获取第一个用户作为创建人
        creator = db.query(User).first()
        if not creator:
            print("错误：数据库中没有用户，请先创建用户")
            return
        
        # 生成30个需求记录
        requirements = []
        for i in range(30):
            # 随机选择各个字段的值
            source = sources[i % len(sources)]
            name = requirement_names[i % len(requirement_names)]
            description = descriptions[i % len(descriptions)]
            status = statuses[i % len(statuses)]
            priority = priorities[i % len(priorities)]
            tag = tags[i % len(tags)]
            
            # 生成计划完成日期（未来30-90天内）
            days_ahead = 30 + (i % 60)
            planned_completion_date = datetime.now() + timedelta(days=days_ahead)
            
            # 随机设置实际完成日期（只有部分需求有实际完成日期）
            actual_completion_date = None
            if i % 5 == 0 and status == "已确认":
                actual_completion_date = datetime.now() - timedelta(days=random.randint(1, 30))
            
            # 创建需求对象
            requirement = Requirement(
                created_by=creator.id,
                source=source,
                name=f"{name} - {i+1}",
                tag_id=tag.id,
                description=f"{description}\n\n详细说明：\n1. 功能需求分析\n2. 技术实现方案\n3. 测试计划\n4. 上线计划",
                status=status,
                priority=priority,
                planned_completion_date=planned_completion_date,
                actual_completion_date=actual_completion_date
            )
            requirements.append(requirement)
        
        # 批量插入需求记录
        db.add_all(requirements)
        db.commit()
        
        print(f"成功插入 {len(requirements)} 条需求记录")
        print("\n需求统计：")
        
        # 统计各状态的需求数量
        for status in statuses:
            count = db.query(Requirement).filter(Requirement.status == status).count()
            print(f"  {status}: {count} 条")
        
        # 统计各优先级的需求数量
        print("\n优先级统计：")
        for priority in priorities:
            count = db.query(Requirement).filter(Requirement.priority == priority).count()
            print(f"  {priority}: {count} 条")
        
        # 统计各来源的需求数量
        print("\n来源统计：")
        for source in sources[:5]:  # 只显示前5个来源
            count = db.query(Requirement).filter(Requirement.source == source).count()
            print(f"  {source}: {count} 条")
        
    except IntegrityError as e:
        db.rollback()
        print(f"错误：插入数据时发生完整性错误 - {e}")
    except Exception as e:
        db.rollback()
        print(f"错误：插入数据时发生错误 - {e}")
    finally:
        db.close()

import random

if __name__ == "__main__":
    print("开始生成需求记录...")
    generate_requirements()
    print("完成！")