from app.db.session import engine
from app.db.base import Base
from app.db import models  # noqa: F401

# IMPORTANT: import models so tables are registered
from app.models.user import User  # noqa: F401
from app.models.tenant import Tenant  # noqa: F401
from app.models.documents import Document  # noqa: F401

def init_db():
    Base.metadata.create_all(bind=engine)
