import os
import shutil
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.deps import get_db
from app.db.session import SessionLocal
import PyPDF2
from app.models.documents import Document

from app.rag.embeddings import generate_embedding
from app.rag.vector_store import add_embedding
from app.rag.chunker import chunk_text

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def process_document(filepath: str, doc_id: str, source_name: str | None = None):
    db: Session = SessionLocal()
    try:
        # ---- Read PDF ----
        reader = PyPDF2.PdfReader(filepath)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        # ---- Split into chunks ----
        chunks = chunk_text(full_text)

        # ---- Generate embeddings & store ----
        for chunk in chunks:
            emb = generate_embedding(chunk)
            add_embedding(emb, chunk, source=source_name)

        document = db.query(Document).filter(Document.id == doc_id).first()
        if document:
            document.status = "processed"
            db.commit()

        print("✅ Document embedded successfully")
    except Exception as e:
        print(f"Error processing document {doc_id}: {e}")
        document = db.query(Document).filter(Document.id == doc_id).first()
        if document:
            document.status = "failed"
            db.commit()
    finally:
        db.close()

@router.post("/upload")
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    doc_id = str(uuid.uuid4())

    save_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = Document(
        id=doc_id,
        tenant_id=current_user["tenant_id"],
        filename=file.filename,
        status="uploaded",
    )
    db.add(document)
    db.commit()

    # ---- Run embedding in background ----
    background_tasks.add_task(process_document, save_path, doc_id, file.filename)

    return {"status": "uploaded"}
