from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import json

from app.core.prompts import INTENT_TOOL_DEFINITIONS, INTENT_ROUTING_PROMPT, TITLE_GEN_PROMPT
from app.services.stream_builder import (
    handle_process_stream, handle_map_stream, handle_rag_stream, handle_chat_stream,
)
from routers.admin import router as admin_router
from database import get_db, SessionLocal
from app.core.llm_client import llm
from utils.auth import AuthHandler
from models import User, Conversation, Message, Resource, ServiceGuide

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def _sse_wrapper(event_gen, convo_id):
    """Wrap a dict event generator into SSE format, saving the AI message on completion."""
    full_answer = ""
    sources = []
    try:
        for event in event_gen:
            if event["type"] == "token":
                full_answer += event["content"]
            elif event["type"] == "meta":
                sources = event.get("sources", [])
            elif event["type"] == "done":
                continue
            yield f"data: {json.dumps(event)}\n\n"
    finally:
        db = SessionLocal()
        try:
            ai_msg = Message(
                convo_id=convo_id, role="ai", content=full_answer,
                sources=json.dumps(sources),
            )
            db.add(ai_msg)
            db.commit()
        finally:
            db.close()

    yield f'data: {json.dumps({"type": "done", "convo_id": convo_id})}\n\n'


class Question(BaseModel):
    question: str

@app.post("/api/chat")
async def chat_endpoint(request: dict, db: Session = Depends(get_db)):
    user_query = request.get("message")
    user_id = request.get("user_id")
    convo_id = request.get("convo_id")
    active_mode = request.get("active_mode", "auto")
    if active_mode not in ("auto", "policy", "map", "service"):
        active_mode = "auto"
    user_lat = request.get("lat")
    user_lng = request.get("lng")

    if not convo_id:
        new_convo = Conversation(user_id=user_id, title="")
        db.add(new_convo)
        db.commit()
        db.refresh(new_convo)
        convo_id = new_convo.id

        title_prompt = TITLE_GEN_PROMPT.format(user_query=user_query)
        generated = llm.ask(title_prompt, system_message="你是标题生成工具，只输出标题文本。")
        if generated and len(generated.strip()) > 1:
            new_convo.title = generated.strip()[:20]
            db.commit()
    
    user_msg = Message(convo_id=convo_id, role="user", content=user_query)
    db.add(user_msg)
    db.commit()

    # 构建对话历史上下文（标准多轮对话格式）
    history = []
    if convo_id:
        history_records = (
            db.query(Message)
            .filter(Message.convo_id == convo_id)
            .order_by(Message.created_at.desc())
            .limit(6)
            .all()
        )
        for msg in reversed(history_records):
            role = "assistant" if msg.role == "ai" else "user"
            history.append({"role": role, "content": msg.content})

    # 意图分析 (Function Calling)
    all_guides = db.query(ServiceGuide.title).all()
    service_list_str = ", ".join([g.title for g in all_guides])
    intent_result = llm.classify_intent(
        user_query,
        tools=INTENT_TOOL_DEFINITIONS,
        system_message=INTENT_ROUTING_PROMPT.format(service_list=service_list_str, active_mode=active_mode),
        history=history,
    )
    func_name = intent_result["name"]
    args = intent_result["arguments"]
    print(f"[Intent] {func_name} {args}")

    try:
        if func_name == "show_process":
            stream = handle_process_stream(db, args.get("service_name", ""), user_query, active_mode, history=history)
        elif func_name == "show_map":
            stream = handle_map_stream(db, args.get("keyword", ""), user_query, active_mode, user_lat, user_lng, history=history)
        elif func_name == "search_policy":
            stream = handle_rag_stream(user_query, active_mode, history=history)
        else:
            stream = handle_chat_stream(user_query, active_mode, history=history)

        return StreamingResponse(
            _sse_wrapper(stream, convo_id),
            media_type="text/event-stream",
        )

    except Exception as e:
        db.rollback()
        print(f"对话链路崩溃: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LLM或业务逻辑异常: {str(e)}")


class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not pwd_context.verify(request.password, user.password):
        return {"message": "Invalid username or password"}
    
    token = AuthHandler.create_access_token({"sub": user.username, "role": user.role, "id": user.id})

    return {"role": user.role, 
            "name": user.username, 
            "id": user.id,
            "avatar": "😉", 
            "token": token}

app.include_router(admin_router)


@app.post("/api/register")
async def register(user_data: dict, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user_data["username"]).first()
    if db_user:
        return {"message": "该用户名已被注册"}
    
    hashed_password = pwd_context.hash(user_data["password"])
    new_user = User(
        username=user_data["username"],
        password=hashed_password,
        role="user",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "message": "注册成功"}


@app.get("/api/conversations")
def get_convos(user_id: int, db: Session = Depends(get_db)):
    return db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.created_at.desc()).all()
   

@app.post("/api/conversations")
def create_convo(user_id: int, title: str, db: Session = Depends(get_db)):
    new_convo = Conversation(user_id=user_id, title=title)
    db.add(new_convo)
    db.commit()
    db.refresh(new_convo)
    return new_convo


@app.get("/api/conversations/{convo_id}/messages")
def get_messages(convo_id: int, db: Session = Depends(get_db)):
    return db.query(Message).filter(Message.convo_id == convo_id).all()


@app.patch("/api/conversations/{convo_id}")
def rename_convo(convo_id: int, title: str, db: Session = Depends(get_db)):
    db_convo = db.query(Conversation).filter(Conversation.id == convo_id).first()
    if not db_convo:
        raise HTTPException(status_code=404, detail="会话不存在")
    db_convo.title = title
    db.commit()
    return {"status": "success"}


@app.delete("/api/conversations/{convo_id}")
def delete_convo(convo_id: int, db: Session = Depends(get_db)):
    db_convo = db.query(Conversation).filter(Conversation.id == convo_id).first()
    if not db_convo:
        raise HTTPException(status_code=404, detail="会话不存在")
    db.query(Message).filter(Message.convo_id == convo_id).delete()
    db.delete(db_convo)
    db.commit()
    return {"status": "success"}
