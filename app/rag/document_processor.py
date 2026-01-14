from PyPDF2 import PdfReader
from app.rag.embeddings import generate_embedding
from app.rag.vector_store import add_embedding

def process_pdf(file_path: str):
    reader = PdfReader(file_path)
    full_text = ""

    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    # Split text into small chunks
    chunks = [full_text[i:i+500] for i in range(0, len(full_text), 500)]

    for chunk in chunks:
        embedding = generate_embedding(chunk)
        add_embedding(embedding, chunk)

    print("✅ Document processed & embeddings stored")
