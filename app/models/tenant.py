from sqlalchemy import Column, String
from app.db.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable= False)
