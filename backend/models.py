from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, ForeignKey, Float, Text
from database import Base
import datetime

def now_without_microseconds():
    return datetime.datetime.now().replace(microsecond=0)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(100))
    role = Column(String(20), default="user")
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'user')", name="check_role_valid"),
    )
    created_at = Column(DateTime, default=now_without_microseconds)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True)
    file_path = Column(String(512))
    file_size = Column(Float)
    status = Column(String(20), default="processing")
    chunk_count = Column(Integer, default=0)
    uploader_id = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime, default=now_without_microseconds)

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=now_without_microseconds)
    updated_at = Column(DateTime, default=now_without_microseconds, onupdate=now_without_microseconds)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    convo_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(20))
    content = Column(Text)
    sources = Column(Text, nullable=True)
    created_at = Column(DateTime, default=now_without_microseconds)

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False) 
    category = Column(String(50), index=True)  
    address = Column(String(255))             
    latlng = Column(String(100), nullable=False)        
    phone = Column(String(50), nullable=True)  
    tags = Column(String(255))
    description = Column(Text, nullable=True)
    status = Column(Integer, default=0, index=True)
    modify_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=now_without_microseconds)
    updated_at = Column(DateTime, default=now_without_microseconds, onupdate=now_without_microseconds) 

class ServiceGuide(Base):
    __tablename__ = "service_guides"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    dept_name = Column(String(100))
    conditions = Column(Text)
    materials = Column(Text)
    flow_steps = Column(Text)
    address = Column(Text)
    latlng = Column(String(100))
    office_time = Column(String(255))
    phone = Column(String(50))
    source_url = Column(String(512))
    modify_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=now_without_microseconds)
