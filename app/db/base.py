from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import models so SQLAlchemy registers tables
from app.models.user import User
from app.models.tenant import Tenant
from app.models.documents import Document
