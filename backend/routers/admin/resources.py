# 资源点管理路由
import os
import datetime
import requests

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import get_db
from models import Resource
from . import verify_admin

load_dotenv()

AMAP_WEB_KEY = os.getenv("AMAP_WEB_KEY")
router = APIRouter()


@router.get("/resources")
def get_admin_resources(
    page: int = 1, size: int = 20,
    category: str = None, status: int = None, keyword: str = None,
    db: Session = Depends(get_db),
):
    """资源点分页列表"""
    query = db.query(Resource)
    if category:
        query = query.filter(Resource.category == category)
    if status is not None:
        query = query.filter(Resource.status == status)
    if keyword:
        query = query.filter(Resource.name.contains(keyword))
    total = query.count()
    items = query.order_by(Resource.updated_at.desc()).offset((page - 1) * size).limit(size).all()
    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/resources/amap-search")
def search_amap_poi(keyword: str, category: str = "", city: str = "大连"):
    """代理高德 POI 搜索，返回格式化数据供前端预览"""
    url = f"https://restapi.amap.com/v3/place/text?keywords={keyword}&types={category}&city={city}&offset=20&page=1&key={AMAP_WEB_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("status") != "1":
            return []
        pois = []
        for p in data.get("pois", []):
            biz_ext = p.get("biz_ext", {})
            pois.append({
                "name": p["name"],
                "address": p.get("address", "") if isinstance(p.get("address"), str) else "",
                "latlng": p["location"],
                "phone": p.get("tel") if isinstance(p.get("tel"), str) else "",
                "tags": p.get("type", ""),
                "description": f"区域:{p.get('adname','')} | 商圈:{p.get('business_area','') if isinstance(p.get('business_area'),str) else '未知'} | 评分:{biz_ext.get('rating','0') if isinstance(biz_ext,dict) else '0'}",
            })
        return pois
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"高德接口调用失败: {str(e)}")


@router.post("/resources/batch-import")
def batch_import_resources(resources: list[dict], db: Session = Depends(get_db), current_admin: dict = Depends(verify_admin)):
    """批量导入资源点到待审核池"""
    admin_id = current_admin.get("id")
    count = 0
    for item in resources:
        if not db.query(Resource).filter(Resource.name == item["name"]).first():
            db.add(Resource(**item, status=0, modify_by=admin_id))
            count += 1
    db.commit()
    return {"status": "success", "imported": count}


@router.delete("/resources/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db), current_admin: dict = Depends(verify_admin)):
    """删除资源点"""
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="该资源点不存在或已被删除")
    try:
        db.delete(res)
        db.commit()
        return {"status": "success", "message": f"资源点【{res.name}】已成功移除", "operator_id": current_admin.get("id")}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/resources/{res_id}")
def update_resource(res_id: int, update_data: dict, db: Session = Depends(get_db), current_admin: dict = Depends(verify_admin)):
    """更新资源点信息"""
    res = db.query(Resource).filter(Resource.id == res_id).first()
    if not res:
        raise HTTPException(status_code=404, detail="资源不存在")
    for key, value in update_data.items():
        if hasattr(res, key) and key != "id":
            setattr(res, key, value)
    res.modify_by = current_admin.get("id")
    res.updated_at = datetime.datetime.now()
    try:
        db.commit()
        return {"status": "success", "message": "更新成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
