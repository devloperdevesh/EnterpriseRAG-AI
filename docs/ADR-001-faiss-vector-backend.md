mkdir -p docs
cat > docs/ADR-001-faiss-vector-backend.md << 'EOF'
# ADR-001: FAISS as Vector Index Backend

**Status:** Accepted  
**Date:** 2026-08-02  
**Author:** prince-pokharna

## Context

EnterpriseRAG-AI uses Apache Arrow as the internal data representation for
the RAG pipeline (FastAPI → Redis Cache → Vector Retrieval → LLM Inference).
The architecture documentation describes an "Arrow-native, zero-copy" design.

However, the vector similarity search layer requires a practical ANN (Approximate
Nearest Neighbour) index. The available options were:

| Option    | Arrow-native? | Production-ready? | Memory overhead |
|-----------|:-------------:|:-----------------:|:---------------:|
| FAISS     | ❌ (NumPy)    | ✅ Yes            | Low             |
| LanceDB   | ✅ Yes        | Partial           | Medium          |
| Qdrant    | Partial       | ✅ Yes            | Medium-high     |
| pgvector  | ❌ (SQL row)  | ✅ Yes            | High            |

## Decision

**Use FAISS** (`faiss-cpu`) as the vector index.

FAISS is the most battle-tested high-performance ANN library available in Python.
It is used in production at Facebook/Meta scale. Its only limitation relevant to
this project is that it accepts `numpy.float32` arrays, not Arrow `RecordBatch`.

This introduces a single, explicit conversion boundary:
Arrow RecordBatch → np.array(dtype=float32) → FAISS index


and on retrieval:

FAISS search result (np.ndarray) → list[str] documents


This is documented as an intentional "escape hatch" from the Arrow-native pipeline.
It is the **only** point where a memory copy occurs. All stages before (embedding
generation, caching) and after (context assembly, LLM inference) remain Arrow-native.

## Consequences

**Positive:**
- Battle-tested performance at scale
- Simple Python API with no additional infrastructure
- Fast in-memory search (sub-millisecond for <10M vectors)

**Negative / Trade-offs:**
- Two memory copies per retrieval (in → FAISS, out → Python list)
- Not zero-copy end-to-end (the project README claim needs this caveat)
- FAISS index is in-memory; not persistent across restarts without `faiss.write_index()`

## Migration Trigger

Migrate from FAISS to LanceDB (or another Arrow-native ANN) if any of these
conditions are met:
1. Vector count exceeds 50M (FAISS in-memory pressure becomes significant)
2. LanceDB reaches production stability with a stable Python API
3. The memory copy overhead is measured to contribute more than 5% of p95 latency

## References

- [FAISS documentation](https://faiss.ai/)
- [LanceDB Arrow-native design](https://lancedb.github.io/lancedb/)
- Issue #146
EOF