from database import Base, engine, SessionLocal
from passlib.context import CryptContext
import models

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def init_db():

    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin:
            hashed_admin_pwd = pwd_context.hash("hanadmin") 
            newadmin = models.User(username="admin", password=hashed_admin_pwd, role="admin")
            db.add(newadmin)
            db.commit()
        else:
            print("Admin user already exists")

if __name__ == "__main__":
    init_db()