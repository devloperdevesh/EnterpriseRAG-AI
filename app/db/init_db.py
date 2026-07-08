from db.session import engine
from db.base import Base
from db import models

# IMPORTANT: import models so tables are registered
from models.user import User
from models.tenant import Tenant
from models.documents import Document

def init_db():
    Base.metadata.create_all(bind=engine)
