from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password


db = SessionLocal()
user = User(
    id="user_1",
    email="admin@test.com",
    hashed_password=hash_password("test123"),
    tenant_id="tenant_1",
    role="admin"
)
db.add(user)
db.commit()
db.close()

print("Test user created successfully.")