# 知识库管理路由
import os
import shutil

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Document
from app.core.vector_engine import engine
from . import verify_admin

router = APIRouter()

# 上传目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload_docs")
async def upload_docs(
    auth_data: dict = Depends(verify_admin),
    file: UploadFile = File(...),
    chunk_size: str = Form(...),
    chunk_overlap: str = Form(...),
    strategy: str = Form("recursive"),
    db: Session = Depends(get_db),
):
    """上传政策文档 → 物理保存 → 向量化入库"""
    # 写入 DB 记录
    new_doc = Document(filename=file.filename, status="processing")
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # 物理保存文件
    save_path = os.path.join(UPLOAD_DIR, f"{new_doc.id}_{file.filename}")
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    new_doc.file_path = save_path
    new_doc.file_size = round(os.path.getsize(save_path) / (1024 * 1024), 2)
    new_doc.uploader_id = 1
    db.commit()

    # 向量化
    try:
        total_chunks = engine.file_to_vector(
            file_path=save_path, chunk_size=int(chunk_size),
            chunk_overlap=int(chunk_overlap), strategy=strategy,
            doc_id=new_doc.id, filename=file.filename,
        )
        new_doc.status = "ready"
        new_doc.chunk_count = total_chunks
        db.commit()
        return {"status": "success", "chunks": total_chunks}
    except Exception as e:
        new_doc.status = "error"
        db.commit()
        print(f"❌ 向量化失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/docs")
def get_docs(db: Session = Depends(get_db)):
    """文档列表（按时间倒序）"""
    return db.query(Document).order_by(Document.id.desc()).all()


@router.delete("/docs/{doc_id}")
def delete_doc(doc_id: int, db: Session = Depends(get_db)):
    """删除文档及其向量数据、物理文件"""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
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
    """预览文档前 10 个分片"""
    data = engine.preview_doc_chunks(doc_id)
    return [{"content": data["documents"][i], "metadata": data["metadatas"][i]} for i in range(len(data["documents"]))]


@router.get("/status")
def get_docs_status(db: Session = Depends(get_db)):
    """知识库统计：文档数、分片数、维度"""
    return {
        "total_docs": db.query(Document).count(),
        "total_chunks": db.query(func.sum(Document.chunk_count)).scalar() or 0,
        "vector_dim": 768,
        "avg_latency": 120 if db.query(Document).count() > 0 else 0,
    }


@router.post("/docs/{doc_id}/rebuild")
async def rebuild_index(
    doc_id: int,
    chunk_size: int = Form(...),
    chunk_overlap: int = Form(...),
    strategy: str = Form("recursive"),
    db: Session = Depends(get_db),
):
    """重建文档索引"""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="原始文件已丢失，无法重构")
    doc.status = "processing"
    db.commit()
    try:
        engine.delete_vector_data(doc_id)
        total_chunks = engine.file_to_vector(
            file_path=doc.file_path, chunk_size=chunk_size,
            chunk_overlap=chunk_overlap, strategy=strategy,
            doc_id=doc.id, filename=doc.filename,
        )
        doc.status = "ready"
        doc.chunk_count = total_chunks
        db.commit()
        return {"status": "success", "new_chunks": total_chunks}
    except Exception as e:
        doc.status = "error"
        db.commit()
        raise HTTPException(status_code=500, detail=f"重构失败: {str(e)}")
