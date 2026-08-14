"""OpenTelemetry-based tracing for RAG pipeline execution and data lineage.

Issue #159: Provides complete visibility into RAG query execution including
retrieval latency, document lineage, LLM execution time, and token consumption.

Implements structured spans for debugging, performance analysis, and audit trails
in enterprise production environments.
"""

import time
from typing import Any, Optional

from opentelemetry import trace, metrics
from opentelemetry.trace import Status, StatusCode

# Get tracer and meter instances
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Create metrics
retrieval_latency = meter.create_histogram(
    "rag.retrieval.latency_ms",
    unit="ms",
    description="Time taken for retrieval operation",
)

llm_latency = meter.create_histogram(
    "rag.llm.latency_ms",
    unit="ms",
    description="Time taken for LLM generation",
)

reranking_latency = meter.create_histogram(
    "rag.reranking.latency_ms",
    unit="ms",
    description="Time taken for chunk reranking",
)

retrieval_chunk_count = meter.create_histogram(
    "rag.retrieval.chunk_count",
    description="Number of chunks retrieved",
)

token_usage = meter.create_histogram(
    "rag.token_usage",
    description="Tokens used per request",
)


class RAGSpanAttributes:
    """Standard attributes for RAG-related spans."""

    # Query attributes
    QUERY_TEXT = "rag.query.text"
    QUERY_LENGTH = "rag.query.length"
    USER_ID = "rag.user.id"
    TENANT_ID = "rag.tenant.id"
    SESSION_ID = "rag.session.id"

    # Retrieval attributes
    RETRIEVAL_TOP_K = "rag.retrieval.top_k"
    RETRIEVAL_CHUNK_COUNT = "rag.retrieval.chunk_count"
    RETRIEVAL_METHOD = "rag.retrieval.method"
    VECTOR_STORE_TYPE = "rag.vector_store.type"

    # Retrieved document attributes
    DOCUMENT_ID = "rag.document.id"
    DOCUMENT_SOURCE = "rag.document.source"
    DOCUMENT_CHUNK_INDEX = "rag.document.chunk_index"
    DOCUMENT_SIMILARITY_SCORE = "rag.document.similarity_score"

    # LLM attributes
    LLM_MODEL = "rag.llm.model"
    LLM_TEMPERATURE = "rag.llm.temperature"
    INPUT_TOKENS = "rag.llm.input_tokens"
    OUTPUT_TOKENS = "rag.llm.output_tokens"
    TOTAL_TOKENS = "rag.llm.total_tokens"

    # Reranking attributes
    RERANKING_MODEL = "rag.reranking.model"
    RERANKING_TOP_N = "rag.reranking.top_n"

    # Status attributes
    CACHE_HIT = "rag.cache.hit"
    ERROR_TYPE = "rag.error.type"
    ERROR_MESSAGE = "rag.error.message"


class RAGTracer:
    """Context manager for tracing RAG pipeline execution."""

    def __init__(self, query: str, user_id: str, tenant_id: str, session_id: Optional[str] = None):
        """Initialize RAG tracer.

        Args:
            query: The user's query string
            user_id: Unique user identifier
            tenant_id: Tenant identifier
            session_id: Optional session identifier for correlation
        """
        self.query = query
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.session_id = session_id
        self.span = None
        self.start_time = None

    def __enter__(self):
        """Start the main RAG request span."""
        self.start_time = time.time()
        self.span = tracer.start_span("rag.request")

        # Set query attributes
        self.span.set_attribute(RAGSpanAttributes.QUERY_TEXT, self.query[:256])  # Limit to 256 chars
        self.span.set_attribute(RAGSpanAttributes.QUERY_LENGTH, len(self.query))
        self.span.set_attribute(RAGSpanAttributes.USER_ID, self.user_id)
        self.span.set_attribute(RAGSpanAttributes.TENANT_ID, self.tenant_id)

        if self.session_id:
            self.span.set_attribute(RAGSpanAttributes.SESSION_ID, self.session_id)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the main RAG request span."""
        if exc_type is not None:
            self.span.set_status(Status(StatusCode.ERROR))
            self.span.set_attribute(RAGSpanAttributes.ERROR_TYPE, exc_type.__name__)
            self.span.set_attribute(RAGSpanAttributes.ERROR_MESSAGE, str(exc_val))
        else:
            self.span.set_status(Status(StatusCode.OK))

        self.span.end()

    def trace_retrieval(self, top_k: int = 10, vector_store: str = "faiss"):
        """Create a span for vector retrieval operation.

        Args:
            top_k: Number of top results to retrieve
            vector_store: Type of vector store being used

        Returns:
            RetrievalSpan context manager
        """
        return RetrievalSpan(self.span, top_k, vector_store)

    def trace_reranking(self, model: str = "cross-encoder", top_n: int = 3):
        """Create a span for reranking operation.

        Args:
            model: Reranking model being used
            top_n: Number of top results after reranking

        Returns:
            RerankerSpan context manager
        """
        return RerankerSpan(self.span, model, top_n)

    def trace_llm_generation(self, model: str, temperature: float = 0.7):
        """Create a span for LLM generation.

        Args:
            model: LLM model being used
            temperature: Temperature parameter for generation

        Returns:
            LLMSpan context manager
        """
        return LLMSpan(self.span, model, temperature)

    def trace_document_retrieval(self, doc_id: str, source: str, chunk_index: int, similarity: float):
        """Add event for each retrieved document.

        Args:
            doc_id: Document identifier
            source: Document source/path
            chunk_index: Index of the chunk within document
            similarity: Similarity score from retrieval
        """
        with tracer.start_as_current_span("rag.document.retrieved") as span:
            span.set_attribute(RAGSpanAttributes.DOCUMENT_ID, doc_id)
            span.set_attribute(RAGSpanAttributes.DOCUMENT_SOURCE, source)
            span.set_attribute(RAGSpanAttributes.DOCUMENT_CHUNK_INDEX, chunk_index)
            span.set_attribute(RAGSpanAttributes.DOCUMENT_SIMILARITY_SCORE, similarity)


class RetrievalSpan:
    """Context manager for vector retrieval operations."""

    def __init__(self, parent_span: Any, top_k: int, vector_store: str):
        self.parent_span = parent_span
        self.top_k = top_k
        self.vector_store = vector_store
        self.span = None
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        self.span = tracer.start_span("rag.retrieval", attributes={
            RAGSpanAttributes.RETRIEVAL_TOP_K: self.top_k,
            RAGSpanAttributes.VECTOR_STORE_TYPE: self.vector_store,
            RAGSpanAttributes.RETRIEVAL_METHOD: "semantic_search",
        })
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.span.set_status(Status(StatusCode.ERROR))
            self.span.set_attribute(RAGSpanAttributes.ERROR_TYPE, exc_type.__name__)
        else:
            self.span.set_status(Status(StatusCode.OK))

        # Record latency metric
        latency_ms = (time.time() - self.start_time) * 1000
        retrieval_latency.record(latency_ms, {"vector_store": self.vector_store})

        self.span.end()

    def set_chunk_count(self, count: int):
        """Record number of chunks retrieved."""
        self.span.set_attribute(RAGSpanAttributes.RETRIEVAL_CHUNK_COUNT, count)
        retrieval_chunk_count.record(count)


class RerankerSpan:
    """Context manager for chunk reranking operations."""

    def __init__(self, parent_span: Any, model: str, top_n: int):
        self.parent_span = parent_span
        self.model = model
        self.top_n = top_n
        self.span = None
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        self.span = tracer.start_span("rag.reranking", attributes={
            RAGSpanAttributes.RERANKING_MODEL: self.model,
            RAGSpanAttributes.RERANKING_TOP_N: self.top_n,
        })
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.span.set_status(Status(StatusCode.ERROR))
        else:
            self.span.set_status(Status(StatusCode.OK))

        # Record latency metric
        latency_ms = (time.time() - self.start_time) * 1000
        reranking_latency.record(latency_ms, {"model": self.model})

        self.span.end()


class LLMSpan:
    """Context manager for LLM generation operations."""

    def __init__(self, parent_span: Any, model: str, temperature: float):
        self.parent_span = parent_span
        self.model = model
        self.temperature = temperature
        self.span = None
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        self.span = tracer.start_span("rag.llm.generation", attributes={
            RAGSpanAttributes.LLM_MODEL: self.model,
            RAGSpanAttributes.LLM_TEMPERATURE: self.temperature,
        })
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.span.set_status(Status(StatusCode.ERROR))
        else:
            self.span.set_status(Status(StatusCode.OK))

        # Record latency metric
        latency_ms = (time.time() - self.start_time) * 1000
        llm_latency.record(latency_ms, {"model": self.model})

        self.span.end()

    def set_token_usage(self, input_tokens: int, output_tokens: int):
        """Record token usage for the LLM generation.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
        """
        total_tokens = input_tokens + output_tokens

        self.span.set_attribute(RAGSpanAttributes.INPUT_TOKENS, input_tokens)
        self.span.set_attribute(RAGSpanAttributes.OUTPUT_TOKENS, output_tokens)
        self.span.set_attribute(RAGSpanAttributes.TOTAL_TOKENS, total_tokens)

        token_usage.record(total_tokens, {"model": self.model})


def trace_cache_hit(query_id: str):
    """Record a cache hit event.

    Args:
        query_id: Identifier for the cached query
    """
    with tracer.start_as_current_span("rag.cache.hit") as span:
        span.set_attribute("cache.query_id", query_id)


def trace_cache_miss(query_id: str):
    """Record a cache miss event.

    Args:
        query_id: Identifier for the query
    """
    with tracer.start_as_current_span("rag.cache.miss") as span:
        span.set_attribute("cache.query_id", query_id)


def get_current_span():
    """Get the current active span for adding events."""
    return trace.get_current_span()
