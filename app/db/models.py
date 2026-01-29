from sqlalchemy import Column, Integer, String, ForeignKey
from add.db.base import Base




class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    role = Column(String, default="user")
