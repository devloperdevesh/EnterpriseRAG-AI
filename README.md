# 🚀 EnterpriseRAG-AI

**EnterpriseRAG-AI** is a **multi-tenant Retrieval Augmented Generation (RAG) platform**
built for **enterprise knowledge systems**.

It enables organizations to securely upload documents, store embeddings,
and query them using LLM-powered RAG — with **tenant/workspace isolation**.

🌐 Live Demo: https://enterpriserag-ai.vercel.app  
⚙️ Backend API: https://enterpriserag-production.up.railway.app

---

## ✨ Key Features

- 🔐 JWT-based Authentication (Signup / Login)
- 🏢 Multi-tenant / Workspace architecture
- 📄 Document upload & ingestion
- 🧠 Vector search using FAISS
- 🤖 LLM-powered RAG querying
- ⚡ FastAPI backend
- 🎨 React + Vite frontend
- ☁️ Deployed on Railway & Vercel

---

## 🧱 Tech Stack

### Backend
- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL**
- **JWT (python-jose)**
- **Passlib (bcrypt)**
- **Sentence Transformers**
- **FAISS**

### Frontend
- **React (Vite)**
- **TypeScript**
- **Axios**
- **Context API**

---

## 📂 Project Structure

```text
EnterpriseRAG-AI/
├── app/                  # FastAPI backend
│   ├── api/              # API routes
│   ├── core/             # Security, config
│   ├── db/               # DB session & init
│   ├── models/           # SQLAlchemy models
│   └── main.py
│
├── frontend/             # React + Vite frontend
│   ├── src/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── context/
│   │   ├── documents/
│   │   ├── pages/
│   │   └── rag/
│
├── scripts/              # Utility scripts
├── requirements.txt
└── README.md

🔐 Authentication Flow
Signup
{
  "email": "user@company.com",
  "password": "test123",
  "tenant_id": "tenant1",
  "role": "user"
}

Login

Returns a JWT access token used for protected APIs.

🧠 How RAG Works 

Documents are uploaded and chunked

Embeddings are generated using Sentence Transformers

Vectors are stored in FAISS

User query → vector search

Relevant context injected into LLM

LLM generates final answer

🧪 Local Development
Backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload


Backend runs on:

http://localhost:8000

Frontend
cd frontend
npm install
npm run dev


Frontend runs on:

http://localhost:5173

🌍 Deployment

Backend → Railway

Frontend → Vercel

CORS configured for both local and production environments.

🛡️ Security Notes

Passwords hashed with bcrypt (72-byte safe limit)

JWT tokens include expiry (exp)

Tenant ID required to enforce isolation

Protected routes via dependency injection

👨‍💻 Author

Devesh Chauhan
AI / Backend Engineer

GitHub: https://github.com/devloperdevesh
