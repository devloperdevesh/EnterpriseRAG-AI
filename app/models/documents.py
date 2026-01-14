from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func

from app.db.session import Base
from app.rag.embeddings import generate_embedding
from app.rag.vector_store import add_embedding


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, index=True, nullable=False)

    filename = Column(String, nullable=False)
    status = Column(String, default="uploaded")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


def process_document(doc_id: str):
    # Placeholder for document processing logic
    text = "Company allowes 20 days paid leave"
    embedding = generate_embedding(text)
    add_embedding(embedding, text)

    print(f"Document {doc_id} embedded and stored.")