# 管理员路由聚合
from fastapi import APIRouter, Depends, HTTPException, Header
from utils.auth import AuthHandler

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# 共享鉴权依赖
async def verify_admin(authorization: str = Header(None)):
    """JWT + role 校验，仅 admin 可访问"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Token")
    token = authorization.split(" ")[1]
    payload = AuthHandler.verify_token(token)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return payload


# 引入子路由模块
from .users import router as _users_router
from .docs import router as _docs_router
from .resources import router as _resources_router

router.include_router(_users_router)
router.include_router(_docs_router)
router.include_router(_resources_router)
