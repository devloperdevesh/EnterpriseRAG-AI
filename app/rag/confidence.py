"""Out-of-domain query detector with configurable confidence threshold.

Prevents the RAG pipeline from hallucinating answers on topics not covered
by the indexed knowledge base. When the top-1 retrieved chunk falls below
the configurable similarity threshold the query is declared out-of-domain
and a clear, honest fallback response is returned instead of being sent to
the LLM.

This module is intentionally decoupled from the LLM and vector store so it
can be unit-tested independently and adjusted without touching either layer.
"""

from dataclasses import dataclass
from typing import Sequence

# Default minimum relevance score required for the query to be considered
# in-domain. Score is in [0, 1] where 1.0 = identical to a stored chunk.
# Tune this value based on your embedding model and corpus density.
DEFAULT_CONFIDENCE_THRESHOLD: float = 0.40

# Message shown to users when the query is out-of-domain.
OUT_OF_DOMAIN_MESSAGE: str = (
    "I could not find sufficiently relevant information in the knowledge base "
    "to answer your question confidently. Please try rephrasing your query or "
    "upload documents that cover this topic."
)


@dataclass(frozen=True)
class DomainCheckResult:
    """Result of the out-of-domain check."""

    is_in_domain: bool
    top_score: float
    threshold: float
    reason: str


def check_domain(
    scores: Sequence[float],
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> DomainCheckResult:
    """Determine whether a query is in-domain based on retrieval scores.

    A query is considered in-domain when the top-1 retrieved chunk achieves
    a relevance score >= ``threshold``. If the retrieval returned no results,
    or the best score is below the threshold, the query is out-of-domain.

    Args:
        scores: Relevance scores of retrieved chunks, highest first.
            Values are in [0, 1]; higher means more relevant.
        threshold: Minimum score for the top chunk to be considered in-domain.

    Returns:
        A :class:`DomainCheckResult` describing the decision.
    """
    if not scores:
        return DomainCheckResult(
            is_in_domain=False,
            top_score=0.0,
            threshold=threshold,
            reason="No relevant documents found in the knowledge base.",
        )

    top_score = max(scores)

    if top_score < threshold:
        return DomainCheckResult(
            is_in_domain=False,
            top_score=top_score,
            threshold=threshold,
            reason=(
                f"Best retrieval score {top_score:.3f} is below the confidence "
                f"threshold of {threshold:.3f}."
            ),
        )

    return DomainCheckResult(
        is_in_domain=True,
        top_score=top_score,
        threshold=threshold,
        reason=f"Top chunk score {top_score:.3f} meets threshold {threshold:.3f}.",
    )


def out_of_domain_response() -> str:
    """Return the standard out-of-domain user-facing message."""
    return OUT_OF_DOMAIN_MESSAGE
