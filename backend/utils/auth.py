from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import os
load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

class AuthHandler:
    @staticmethod
    def create_access_token(data: dict):
        """生成 JWT Token"""
        to_encode = data.copy()
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str):
        """验证 Token 并返回载荷数据"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

