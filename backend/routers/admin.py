import os
import shutil
import requests

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Document, User, Resource, Conversation, Message
from passlib.context import CryptContext
from app.core.vector_engine import engine
from utils.auth import AuthHandler
from dotenv import load_dotenv

load_dotenv()

AMAP_WEB_KEY = os.getenv("AMAP_WEB_KEY")

router = APIRouter(prefix="/api/admin", tags=["Admin"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # 获取 backend 目录
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

async def verify_admin(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Token")
    
    token = authorization.split(" ")[1]
    payload = AuthHandler.verify_token(token)
    
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return payload


@router.get("/users")
def get_all_users(
    keyword: str = None,
    role: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if keyword:
        query = query.filter(User.username.contains(keyword))
    if role:
        query = query.filter(User.role == role)

    users = query.all()

    result = []
    for u in users:
        convo_count = (
            db.query(func.count(Conversation.id))
            .filter(Conversation.user_id == u.id)
            .scalar()
        )
        msg_count = (
            db.query(func.count(Message.id))
            .join(Conversation)
            .filter(Conversation.user_id == u.id)
            .scalar()
        )
        result.append(
            {
                "id": u.id,
                "username": u.username,
                "role": u.role,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "convo_count": convo_count,
                "msg_count": msg_count,
            }
        )
    return result


@router.delete("/users/{user_id}")
def del_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(verify_admin),
):
    if current_admin.get("id") == user_id:
        raise HTTPException(status_code=403, detail="不能删除自己的账户")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(user)
    db.commit()
    return {"message": "用户已删除"}


@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(verify_admin),
):
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
@router.post("/upload_docs")
async def uploadDocs(
    auth_data: dict = Depends(verify_admin), 
    file: UploadFile = File(...),
    chunk_size: str = Form(...),
    chunk_overlap: str = Form(...),
    strategy: str = Form("recursive"),
    db: Session = Depends(get_db)
    ):
    
    new_doc = Document(filename=file.filename, status="processing")
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # 2. 物理保存 (仅操作 IO)
    save_path = os.path.join(UPLOAD_DIR, f"{new_doc.id}_{file.filename}")
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    new_doc.file_path = save_path # 更新路径
    new_doc.file_size = round(os.path.getsize(save_path) / (1024 * 1024), 2)
    new_doc.uploader_id = 1 
    db.commit()

    try:
        chunk_size = int(chunk_size)
        chunk_overlap = int(chunk_overlap)
        # 3. 调用 Service 处理 (解耦点：路由不关心算法细节)
        total_chunks = engine.file_to_vector(
            file_path=save_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=strategy,
            doc_id=new_doc.id,
            filename=file.filename
        )

        # 4. 更新状态
        new_doc.status = "ready"
        new_doc.chunk_count = total_chunks
        db.commit()
        return {"status": "success", "chunks": total_chunks}

    except Exception as e:
        new_doc.status = "error"
        db.commit()
        print(f"❌ 向量化解析崩溃! 错误详情: {str(e)}") 
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/docs")
def get_docs(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.id.desc()).all()
    return docs

@router.delete("/docs/{doc_id}")
def delete_doc(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        engine.delete_vector_data(doc_id)
        if doc.file_path and os.path.exists(doc.file_path):
            os.remove(doc.file_path)
       
        db.delete(doc)
        db.commit()
        return {"message": "知识库关联数据已彻底清除"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/docs/{doc_id}/preview")
def preview_doc(doc_id: int):
    data = engine.preview_doc_chunks(doc_id)
    chunks = []
    for i in range(len(data["documents"])):
        chunks.append({
            "content": data["documents"][i],
            "metadata": data["metadatas"][i]
        })
    return chunks

@router.get("/status")
def get_docs_status(db: Session = Depends(get_db)):
    total_docs = db.query(Document).count()
    total_chunks = db.query(func.sum(Document.chunk_count), 0).scalar()
    vector_dim = 768
    avg_latency = 120 if total_docs > 0 else 0

    return {
        "total_docs": total_docs,
        "total_chunks": total_chunks,
        "vector_dim": vector_dim,
        "avg_latency": avg_latency
    }

@router.post("/docs/{doc_id}/rebuild")
async def rebuild_index(
    doc_id: int, 
    chunk_size: int = Form(...),
    chunk_overlap: int = Form(...),
    strategy: str = Form("recursive"),
    db: Session = Depends(get_db)
):
    # 1. 查找元数据
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="原始文件已丢失，无法重构")

    # 2. 状态锁定
    doc.status = "processing"
    db.commit()

    try:
        engine.delete_vector_data(doc_id)

        total_chunks = engine.file_to_vector(
            file_path=doc.file_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=strategy,
            doc_id=doc.id,
            filename=doc.filename
        )

        # 5. 更新元数据
        doc.status = "ready"
        doc.chunk_count = total_chunks
        db.commit()
        
        return {"status": "success", "new_chunks": total_chunks}
        
    except Exception as e:
        doc.status = "error"
        db.commit()
        raise HTTPException(status_code=500, detail=f"重构失败: {str(e)}")
    
@router.get("/resources")
def get_admin_resources(
    page: int = 1,
    size: int = 20, 
    category: str = None, 
    status: int = None,
    keyword: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(Resource)

    if category:
        query = query.filter(Resource.category == category)
    if status is not None:
        query = query.filter(Resource.status == status)
    if keyword:
        query = query.filter(Resource.name.contains(keyword))

    total = query.count()
    items = query.order_by(Resource.updated_at.desc()) \
                 .offset((page - 1) * size) \
                 .limit(size) \
                 .all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size
    }

@router.get("/resources/amap-search")
def search_amap_poi(keyword: str, category: str="", city: str = "大连"):
    """
    代理请求高德接口，仅返回数据给前端预览，不存库
    """
    url = f"https://restapi.amap.com/v3/place/text?keywords={keyword}&types={category}&city={city}&offset=20&page=1&key={AMAP_WEB_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        if data.get('status') == '1':
            pois = []
            for p in data.get('pois', []):
                raw_tel = p.get('tel')
                safe_phone = raw_tel if isinstance(raw_tel, str) else ""
                raw_type = p.get('type', '')
                
                # 3. 构造复合 description (包含行政区、商圈、评分)
                biz_ext = p.get('biz_ext', {})
                rating = biz_ext.get('rating') if isinstance(biz_ext, dict) else "0"
                district = p.get('adname', '')
                business = p.get('business_area', '')
                # 将元数据转化为结构化描述字符串
                description = f"区域:{district} | 商圈:{business if isinstance(business, str) else '未知'} | 评分:{rating}"
                
                pois.append({
                    "name": p['name'],
                    "address": p.get('address', '') if isinstance(p.get('address'), str) else "",
                    "latlng": p['location'],
                    "phone": safe_phone,
                    "tags": raw_type,
                    "description": description,
                })
            return pois
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"高德接口调用失败: {str(e)}")

@router.post("/resources/batch-import")
def batch_import_resources(
    resources: list[dict], 
    db: Session = Depends(get_db),
    current_admin: dict = Depends(verify_admin)
):
    admin_id = current_admin.get("id")
    count = 0

    for item in resources:
        # 简单查重
        exists = db.query(Resource).filter(Resource.name == item['name']).first()
        if not exists:
            new_res = Resource(
                **item,
                status=0,          # 初始为“待审核”
                modify_by=admin_id,  
            )
            db.add(new_res)
            count += 1
    db.commit()
    return {"status": "success", "imported": count}



@router.delete("/resources/{resource_id}")
def delete_resource(
    resource_id: int, 
    db: Session = Depends(get_db),
    # [接洽点]：必须经过管理员身份验证，防止接口被非法调用
    current_admin: dict = Depends(verify_admin) 
):
    # 1. 查找目标记录
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not db_resource:
        raise HTTPException(status_code=404, detail="该资源点不存在或已被删除")

    try:
        # 2. 执行物理删除
        db.delete(db_resource)
        db.commit()
        
        # 3. 返回操作结果
        return {
            "status": "success", 
            "message": f"资源点【{db_resource.name}】已成功移除",
            "operator_id": current_admin.get("id") # 返回操作人ID备查
        }
    except Exception as e:
        db.rollback()
        print(f"❌ 删除资源失败: {str(e)}")
        raise HTTPException(status_code=500, detail="系统内部错误，删除失败")
    
@router.patch("/resources/{res_id}")
def update_resource(
    res_id: int, 
    update_data: dict, 
    db: Session = Depends(get_db),
    current_admin: dict = Depends(verify_admin)
):
    # 1. 查找资源
    db_res = db.query(Resource).filter(Resource.id == res_id).first()
    if not db_res:
        raise HTTPException(status_code=404, detail="资源不存在")

    # 2. 动态更新字段 (排除掉 id 等不可变字段)
    for key, value in update_data.items():
        if hasattr(db_res, key) and key != "id":
            setattr(db_res, key, value)
    
    # 3. 强制注入审计信息
    admin_id = current_admin.get("id") if isinstance(current_admin, dict) else current_admin.id
    db_res.modify_by = admin_id

    import datetime
    db_res.updated_at = datetime.datetime.now()

    try:
        db.commit()
        return {"status": "success", "message": "更新成功"}
    except Exception as e:
        db.rollback()
        print(f"❌ 更新失败详情: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))