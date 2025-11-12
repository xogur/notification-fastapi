from sqlalchemy import Column, Integer, String, DateTime, text
from app.database.conn import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, server_default="active")
    created_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
