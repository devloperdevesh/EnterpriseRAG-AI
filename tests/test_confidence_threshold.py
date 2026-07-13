"""Tests for the out-of-domain confidence threshold checker."""

import pytest

from app.rag.confidence import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    DomainCheckResult,
    check_domain,
    out_of_domain_response,
)


class TestCheckDomain:
    def test_empty_scores_is_out_of_domain(self):
        result = check_domain([])
        assert result.is_in_domain is False
        assert result.top_score == 0.0

    def test_score_above_threshold_is_in_domain(self):
        result = check_domain([0.85, 0.70, 0.60], threshold=0.40)
        assert result.is_in_domain is True
        assert result.top_score == 0.85

    def test_score_equal_to_threshold_is_in_domain(self):
        result = check_domain([0.40], threshold=0.40)
        assert result.is_in_domain is True

    def test_score_below_threshold_is_out_of_domain(self):
        result = check_domain([0.25, 0.18], threshold=0.40)
        assert result.is_in_domain is False
        assert result.top_score == 0.25

    def test_custom_threshold_respected(self):
        result = check_domain([0.55], threshold=0.70)
        assert result.is_in_domain is False

    def test_returns_domain_check_result_type(self):
        result = check_domain([0.9])
        assert isinstance(result, DomainCheckResult)

    def test_threshold_field_matches_input(self):
        result = check_domain([0.5], threshold=0.6)
        assert result.threshold == 0.6

    def test_reason_mentions_threshold_when_out_of_domain(self):
        result = check_domain([0.10], threshold=0.40)
        assert "0.400" in result.reason or "threshold" in result.reason.lower()

    def test_uses_default_threshold_when_not_specified(self):
        result = check_domain([DEFAULT_CONFIDENCE_THRESHOLD - 0.01])
        assert result.is_in_domain is False

        result = check_domain([DEFAULT_CONFIDENCE_THRESHOLD])
        assert result.is_in_domain is True


def test_out_of_domain_response_is_non_empty_string():
    msg = out_of_domain_response()
    assert isinstance(msg, str)
    assert len(msg) > 20
