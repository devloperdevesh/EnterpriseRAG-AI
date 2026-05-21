import uuid
import os
import shutil
import io

from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import PyPDF2

from app.core.dependencies import get_current_user
from app.db.deps import get_db
from app.models.documents import Document

from app.rag.embeddings import generate_embedding
from app.rag.vector_store import add_embedding
from app.rag.chunker import chunk_text, chunk_text_with_metadata

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_pdf_text(filepath: str) -> str:
    reader = PyPDF2.PdfReader(filepath)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    return full_text


def _process_and_embed(filepath: str) -> None:
    """Background task: chunk PDF and store embeddings."""
    full_text = _extract_pdf_text(filepath)
    chunks = chunk_text(full_text)
    for chunk in chunks:
        emb = generate_embedding(chunk)
        add_embedding(emb, chunk)
    print("✅ Document embedded successfully")


# ---------------------------------------------------------------------------
# Upload endpoint
# ---------------------------------------------------------------------------

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

    background_tasks.add_task(_process_and_embed, save_path)

    return {"status": "uploaded", "doc_id": doc_id}


# ---------------------------------------------------------------------------
# Chunking visualization endpoint  (Issue #1)
# ---------------------------------------------------------------------------

@router.post("/preview-chunks")
async def preview_chunks(
    file: UploadFile = File(...),
    chunk_size: int = 500,
    overlap: int = 50,
    current_user=Depends(get_current_user),
):
    """
    Upload a PDF and receive a real-time chunk breakdown for visualization.
    Returns metadata for every chunk: index, preview text, word count,
    char count, and word-position range.

    Used by the frontend chunking visualization UI (Issue #1).
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Read file bytes in-memory (no disk write needed for preview)
    contents = await file.read()
    reader = PyPDF2.PdfReader(io.BytesIO(contents))

    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    if not full_text.strip():
        raise HTTPException(status_code=422, detail="Could not extract text from PDF.")

    chunks = chunk_text_with_metadata(
        full_text,
        chunk_size=chunk_size,
        overlap=overlap,
    )

    total_words = len(full_text.split())

    return {
        "total_words": total_words,
        "total_chunks": len(chunks),
        "chunk_size": chunk_size,
        "overlap": overlap,
        "chunks": [
            {
                "index": c.index,
                "preview": c.text[:200] + ("…" if len(c.text) > 200 else ""),
                "full_text": c.text,
                "word_count": c.word_count,
                "char_count": c.char_count,
                "start_word": c.start_word,
                "end_word": c.end_word,
            }
            for c in chunks
        ],
    }
