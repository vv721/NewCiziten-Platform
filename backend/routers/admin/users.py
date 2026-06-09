# 用户管理路由
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from passlib.context import CryptContext

from database import get_db
from models import User, Conversation, Message
from . import verify_admin

router = APIRouter()


@router.get("/users")
def get_all_users(keyword: str = None, role: str = None, db: Session = Depends(get_db)):
    """用户列表（含会话数/消息数统计）"""
    query = db.query(User)
    if keyword:
        query = query.filter(User.username.contains(keyword))
    if role:
        query = query.filter(User.role == role)

    result = []
    for u in query.all():
        convo_count = db.query(func.count(Conversation.id)).filter(Conversation.user_id == u.id).scalar()
        msg_count = db.query(func.count(Message.id)).join(Conversation).filter(Conversation.user_id == u.id).scalar()
        result.append({
            "id": u.id, "username": u.username, "role": u.role,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "convo_count": convo_count, "msg_count": msg_count,
        })
    return result


@router.delete("/users/{user_id}")
def del_user(user_id: int, db: Session = Depends(get_db), current_admin: dict = Depends(verify_admin)):
    """删除用户（不可删除自己）"""
    if current_admin.get("id") == user_id:
        raise HTTPException(status_code=403, detail="不能删除自己的账户")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(user)
    db.commit()
    return {"message": "用户已删除"}


@router.post("/users/{user_id}/reset-password")
def reset_user_password(user_id: int, data: dict, db: Session = Depends(get_db), current_admin: dict = Depends(verify_admin)):
    """管理员重置用户密码"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    new_password = data.get("new_password", "").strip()
    if len(new_password) < 4:
        raise HTTPException(status_code=400, detail="密码至少4位")
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    user.password = pwd_context.hash(new_password)
    db.commit()
    return {"status": "success", "message": "密码已重置"}
