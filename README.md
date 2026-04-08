# EnterpriseRAG AI

Scalable multi-tenant AI knowledge system for large-scale document intelligence using Retrieval-Augmented Generation (RAG).

---

## Overview

EnterpriseRAG AI is a distributed backend system designed to process and query large document datasets using semantic retrieval and LLM-based response generation.

The system focuses on high-concurrency performance, tenant isolation, and predictable behavior under load.

---

## Live System

- Frontend: https://enterpriserag-ai.vercel.app  
- Backend API: https://enterpriserag-production.up.railway.app  

---

## Problem

Traditional document systems struggle with:

- Inefficient keyword-based search  
- Lack of contextual understanding  
- Hallucinated responses due to missing grounding  

---

## Solution

The system addresses these challenges using:

- Semantic vector search (FAISS)  
- Retrieval-Augmented Generation (RAG)  
- Multi-tenant architecture with strict isolation  

This enables context-aware and scalable document querying.

---

## Key Features

### Authentication and Security

- JWT-based authentication with expiry  
- Secure password hashing (bcrypt)  
- Tenant-aware access control  

---

### Multi-Tenant Architecture

- Workspace-level isolation  
- No cross-tenant data leakage  
- SaaS-ready backend design  

---

### Document Processing Pipeline

- Document upload and ingestion  
- Context-aware chunking  
- Embedding generation (Sentence Transformers)  
- Vector indexing using FAISS  

---

### RAG Query Engine

- Semantic retrieval (top-K search)  
- Context injection into LLM  
- Grounded response generation  

---

### Performance

- Handles 100K+ documents  
- Tested under high-concurrency load  
- ~40% latency reduction via system optimizations  
- Designed toward high-throughput scalability  

---

## Tech Stack

### Backend

- FastAPI  
- PostgreSQL  
- SQLAlchemy  
- FAISS  
- Sentence Transformers  
- JWT (python-jose)  
- Passlib (bcrypt)  

---

### Frontend

- React (Vite)  
- TypeScript  
- Axios  
- Zustand  

---

## System Architecture

Client → CDN → Load Balancer → FastAPI (Async API Layer)  
→ Cache Layer (Redis - planned)  
→ FAISS (Vector Search)  
→ LLM (Response Generation)  

---

## RAG Flow

1. Documents are uploaded  
2. Content is chunked into segments  
3. Embeddings are generated  
4. Stored in FAISS vector index  
5. User query is embedded  
6. Top-K relevant chunks retrieved  
7. LLM generates grounded response  

---

## Load Testing

- Tool: k6  
- Duration: 10 minutes sustained traffic  

Results:

- ~850 req/sec throughput  
- p95 latency: ~480ms  
- p99 latency: ~720ms  
- Error rate: <1%  

---

## Engineering Highlights

- Designed async backend for non-blocking request handling  
- Implemented backpressure-aware request flow  
- Optimized latency using retrieval and processing strategies  
- Built system resilient to load spikes and partial failures  

---

## Deployment

- Frontend: Vercel  
- Backend: Railway  
- Database: PostgreSQL  

---

## Security

- JWT authentication with expiry  
- Secure password hashing  
- Tenant-based isolation  
- Protected API routes  

---

## Future Enhancements

- Redis caching layer  
- Observability (metrics and logging)  
- Hybrid search (keyword + vector)  
- Streaming responses (WebSockets)  
- Kubernetes-based deployment  
- Multi-LLM support  

---

## Author

Devesh Chauhan  
Backend Systems Engineer — Distributed Systems — AI Infrastructure  

GitHub: https://github.com/devloperdevesh  

---

## Summary

This project demonstrates the design of a production-oriented distributed system combining retrieval systems, backend engineering, and real-world performance considerations.

The focus is on scalability, system behavior under load, and engineering trade-offs rather than isolated feature development.
