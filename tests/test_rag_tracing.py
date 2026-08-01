"""Tests for OpenTelemetry-based RAG data lineage tracing (Issue #159)."""

from unittest.mock import MagicMock, patch

import pytest

from app.observability.rag_tracing import (
    LLMSpan,
    RAGSpanAttributes,
    RAGTracer,
    RerankerSpan,
    RetrievalSpan,
    trace_cache_hit,
    trace_cache_miss,
)


class TestRAGTracer:
    """Tests for main RAG tracer."""

    def test_rag_tracer_initialization(self):
        """Should initialize RAG tracer with query and user info."""
        tracer = RAGTracer(
            query="What is machine learning?",
            user_id="user123",
            tenant_id="tenant456",
            session_id="session789",
        )

        assert tracer.query == "What is machine learning?"
        assert tracer.user_id == "user123"
        assert tracer.tenant_id == "tenant456"
        assert tracer.session_id == "session789"

    @patch("app.observability.rag_tracing.tracer")
    def test_rag_tracer_context_manager(self, mock_tracer):
        """Should create and manage span context correctly."""
        mock_span = MagicMock()
        mock_tracer.start_span.return_value = mock_span

        with RAGTracer(
            query="test query",
            user_id="user123",
            tenant_id="tenant456",
        ) as rag_tracer:
            assert rag_tracer.span is not None

        # Verify span was ended
        mock_span.end.assert_called_once()
        # Verify attributes were set
        assert mock_span.set_attribute.called

    @patch("app.observability.rag_tracing.tracer")
    def test_rag_tracer_error_handling(self, mock_tracer):
        """Should set error status on exception."""
        mock_span = MagicMock()
        mock_tracer.start_span.return_value = mock_span

        try:
            with RAGTracer(
                query="test query",
                user_id="user123",
                tenant_id="tenant456",
            ):
                raise ValueError("Test error")
        except ValueError:
            pass

        # Verify error status was set
        mock_span.set_status.assert_called()

    @patch("app.observability.rag_tracing.tracer")
    def test_rag_tracer_query_text_truncation(self, mock_tracer):
        """Should truncate long query text for span attributes."""
        mock_span = MagicMock()
        mock_tracer.start_span.return_value = mock_span

        long_query = "a" * 500  # 500 characters

        with RAGTracer(
            query=long_query,
            user_id="user123",
            tenant_id="tenant456",
        ):
            pass

        # Find the call that sets query text
        for call in mock_span.set_attribute.call_args_list:
            if call[0][0] == RAGSpanAttributes.QUERY_TEXT:
                # Should be truncated to 256 chars
                assert len(call[0][1]) == 256


class TestRetrievalSpan:
    """Tests for vector retrieval spans."""

    @patch("app.observability.rag_tracing.tracer")
    @patch("app.observability.rag_tracing.retrieval_latency")
    def test_retrieval_span_creation(self, mock_latency, mock_tracer):
        """Should create retrieval span with correct attributes."""
        mock_parent_span = MagicMock()
        mock_span = MagicMock()
        mock_tracer.start_span.return_value = mock_span

        with RetrievalSpan(mock_parent_span, top_k=10, vector_store="faiss"):
            pass

        # Verify span was created with attributes
        mock_tracer.start_span.assert_called()

    @patch("app.observability.rag_tracing.tracer")
    @patch("app.observability.rag_tracing.retrieval_latency")
    def test_retrieval_span_chunk_count(self, mock_latency, mock_tracer):
        """Should record chunk count in retrieval span."""
        mock_parent_span = MagicMock()
        mock_span = MagicMock()
        mock_tracer.start_span.return_value = mock_span

        with RetrievalSpan(mock_parent_span, top_k=10, vector_store="faiss") as span:
            span.set_chunk_count(5)

        # Verify chunk count was set
        assert mock_span.set_attribute.called


class TestRerankerSpan:
    """Tests for chunk reranking spans."""

    @patch("app.observability.rag_tracing.tracer")
    @patch("app.observability.rag_tracing.reranking_latency")
    def test_reranker_span_creation(self, mock_latency, mock_tracer):
        """Should create reranker span with correct attributes."""
        mock_parent_span = MagicMock()
        mock_span = MagicMock()
        mock_tracer.start_span.return_value = mock_span

        with RerankerSpan(mock_parent_span, model="cross-encoder", top_n=3):
            pass

        mock_tracer.start_span.assert_called()


class TestLLMSpan:
    """Tests for LLM generation spans."""

    @patch("app.observability.rag_tracing.tracer")
    @patch("app.observability.rag_tracing.llm_latency")
    def test_llm_span_creation(self, mock_latency, mock_tracer):
        """Should create LLM span with correct attributes."""
        mock_parent_span = MagicMock()
        mock_span = MagicMock()
        mock_tracer.start_span.return_value = mock_span

        with LLMSpan(mock_parent_span, model="gpt-3.5-turbo", temperature=0.7):
            pass

        mock_tracer.start_span.assert_called()

    @patch("app.observability.rag_tracing.tracer")
    @patch("app.observability.rag_tracing.llm_latency")
    @patch("app.observability.rag_tracing.token_usage")
    def test_llm_span_token_usage(self, mock_token_usage, mock_latency, mock_tracer):
        """Should record token usage in LLM span."""
        mock_parent_span = MagicMock()
        mock_span = MagicMock()
        mock_tracer.start_span.return_value = mock_span

        with LLMSpan(mock_parent_span, model="gpt-3.5-turbo", temperature=0.7) as span:
            span.set_token_usage(input_tokens=100, output_tokens=50)

        # Verify tokens were set
        mock_span.set_attribute.assert_called()
        # Verify metric was recorded
        mock_token_usage.record.assert_called()


class TestCacheTracing:
    """Tests for cache hit/miss tracing."""

    @patch("app.observability.rag_tracing.tracer")
    def test_trace_cache_hit(self, mock_tracer):
        """Should trace cache hit event."""
        mock_span = MagicMock()
        mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

        trace_cache_hit("query123")

        mock_tracer.start_as_current_span.assert_called()

    @patch("app.observability.rag_tracing.tracer")
    def test_trace_cache_miss(self, mock_tracer):
        """Should trace cache miss event."""
        mock_span = MagicMock()
        mock_tracer.start_as_current_span.return_value.__enter__.return_value = mock_span

        trace_cache_miss("query123")

        mock_tracer.start_as_current_span.assert_called()


class TestSpanAttributes:
    """Tests for RAG span attribute constants."""

    def test_span_attributes_exist(self):
        """Should have all required span attributes defined."""
        # Query attributes
        assert hasattr(RAGSpanAttributes, "QUERY_TEXT")
        assert hasattr(RAGSpanAttributes, "QUERY_LENGTH")
        assert hasattr(RAGSpanAttributes, "USER_ID")
        assert hasattr(RAGSpanAttributes, "TENANT_ID")

        # Retrieval attributes
        assert hasattr(RAGSpanAttributes, "RETRIEVAL_TOP_K")
        assert hasattr(RAGSpanAttributes, "RETRIEVAL_CHUNK_COUNT")
        assert hasattr(RAGSpanAttributes, "VECTOR_STORE_TYPE")

        # Document attributes
        assert hasattr(RAGSpanAttributes, "DOCUMENT_ID")
        assert hasattr(RAGSpanAttributes, "DOCUMENT_SOURCE")
        assert hasattr(RAGSpanAttributes, "DOCUMENT_SIMILARITY_SCORE")

        # LLM attributes
        assert hasattr(RAGSpanAttributes, "LLM_MODEL")
        assert hasattr(RAGSpanAttributes, "INPUT_TOKENS")
        assert hasattr(RAGSpanAttributes, "OUTPUT_TOKENS")
        assert hasattr(RAGSpanAttributes, "TOTAL_TOKENS")


class TestIntegrationScenario:
    """Integration tests for complete RAG tracing scenario."""

    @patch("app.observability.rag_tracing.tracer")
    def test_full_rag_tracing_scenario(self, mock_tracer):
        """Should trace complete RAG pipeline execution."""
        mock_span = MagicMock()
        mock_retrieval_span = MagicMock()
        mock_reranker_span = MagicMock()
        mock_llm_span = MagicMock()

        # Setup mock return values
        mock_tracer.start_span.side_effect = [
            mock_span,  # Main RAG span
            mock_retrieval_span,  # Retrieval span
            mock_reranker_span,  # Reranker span
            mock_llm_span,  # LLM span
        ]

        with RAGTracer(
            query="What is AI?",
            user_id="user123",
            tenant_id="tenant456",
            session_id="session789",
        ) as rag_tracer:
            # Simulate retrieval
            with rag_tracer.trace_retrieval(top_k=10, vector_store="faiss") as ret:
                ret.set_chunk_count(8)

            # Simulate reranking
            with rag_tracer.trace_reranking(model="cross-encoder", top_n=3):
                pass

            # Simulate LLM generation
            with rag_tracer.trace_llm_generation(model="gpt-3.5-turbo") as llm:
                llm.set_token_usage(input_tokens=200, output_tokens=100)

        # Verify all spans were created
        assert mock_tracer.start_span.called
