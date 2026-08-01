"""Tests for token budget monitoring and management (Issue #160)."""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from app.core.token_budget import (
    BudgetStatus,
    TokenUsage,
    _get_budget_status,
    check_budget_limit,
    get_budget_metrics,
    set_tenant_budget,
    track_token_usage,
)


class TestTokenUsageTracking:
    """Tests for token usage tracking."""

    @pytest.mark.asyncio
    async def test_track_token_usage(self):
        """Should successfully track token usage and calculate costs."""
        with patch("app.core.token_budget.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hincrby = AsyncMock()
            mock_redis.hincrbyfloat = AsyncMock()
            mock_redis.expire = AsyncMock()
            mock_redis_factory.return_value = mock_redis

            usage = await track_token_usage(
                tenant_id="tenant123",
                user_id="user123",
                api_key_id="key123",
                input_tokens=100,
                output_tokens=50,
                model="gpt-3.5-turbo",
            )

            assert usage.input_tokens == 100
            assert usage.output_tokens == 50
            assert usage.total_tokens == 150
            assert usage.model == "gpt-3.5-turbo"
            assert usage.estimated_cost > 0

    @pytest.mark.asyncio
    async def test_track_token_usage_with_gpt4(self):
        """Should use correct pricing for GPT-4."""
        with patch("app.core.token_budget.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hincrby = AsyncMock()
            mock_redis.hincrbyfloat = AsyncMock()
            mock_redis.expire = AsyncMock()
            mock_redis_factory.return_value = mock_redis

            usage = await track_token_usage(
                tenant_id="tenant123",
                user_id="user123",
                api_key_id="key123",
                input_tokens=1000,
                output_tokens=1000,
                model="gpt-4",
            )

            # GPT-4: input=$0.03/1K, output=$0.06/1K
            # Expected: 1000*0.03/1000 + 1000*0.06/1000 = 0.03 + 0.06 = 0.09
            assert usage.estimated_cost == pytest.approx(0.09)

    @pytest.mark.asyncio
    async def test_track_token_usage_redis_timeout(self):
        """Should not break on Redis timeout."""
        with patch("app.core.token_budget.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hincrby = AsyncMock(side_effect=asyncio.TimeoutError())
            mock_redis_factory.return_value = mock_redis

            # Should not raise, just return usage
            usage = await track_token_usage(
                tenant_id="tenant123",
                user_id="user123",
                api_key_id="key123",
                input_tokens=100,
                output_tokens=50,
            )

            assert usage.total_tokens == 150


class TestBudgetLimitChecking:
    """Tests for budget limit checking."""

    @pytest.mark.asyncio
    async def test_check_budget_within_limits(self):
        """Should return True when usage is within budget."""
        with patch("app.core.token_budget.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hgetall = AsyncMock(
                side_effect=[
                    {"tokens_used": "50000"},  # First call for budget_key
                    {"monthly_limit": "1000000"},  # Second call for config_key
                ]
            )
            mock_redis_factory.return_value = mock_redis

            is_within_budget, status = await check_budget_limit("tenant123")

            assert is_within_budget is True
            assert status == BudgetStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_check_budget_exceeded(self):
        """Should return False when budget is exceeded."""
        with patch("app.core.token_budget.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hgetall = AsyncMock(
                side_effect=[
                    {"tokens_used": "1100000"},  # Over limit
                    {"monthly_limit": "1000000"},
                ]
            )
            mock_redis_factory.return_value = mock_redis

            is_within_budget, status = await check_budget_limit("tenant123")

            assert is_within_budget is False
            assert status == BudgetStatus.EXCEEDED

    @pytest.mark.asyncio
    async def test_check_budget_warning_status(self):
        """Should return warning status at 70-90% usage."""
        with patch("app.core.token_budget.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hgetall = AsyncMock(
                side_effect=[
                    {"tokens_used": "850000"},  # 85% of 1M
                    {"monthly_limit": "1000000"},
                ]
            )
            mock_redis_factory.return_value = mock_redis

            is_within_budget, status = await check_budget_limit("tenant123")

            assert is_within_budget is True
            assert status == BudgetStatus.WARNING


class TestSetTenantBudget:
    """Tests for setting tenant budgets."""

    @pytest.mark.asyncio
    async def test_set_tenant_budget(self):
        """Should successfully configure tenant budget."""
        with patch("app.core.token_budget.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hset = AsyncMock(return_value=1)
            mock_redis.expire = AsyncMock(return_value=True)
            mock_redis_factory.return_value = mock_redis

            result = await set_tenant_budget(
                tenant_id="tenant123",
                monthly_limit=500000,
                budget_limit_usd=500,
            )

            assert result is True
            mock_redis.hset.assert_called_once()
            mock_redis.expire.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_tenant_budget_redis_error(self):
        """Should return False on Redis error."""
        with patch("app.core.token_budget.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hset = AsyncMock(side_effect=Exception("Redis error"))
            mock_redis_factory.return_value = mock_redis

            result = await set_tenant_budget(
                tenant_id="tenant123",
                monthly_limit=500000,
            )

            assert result is False


class TestGetBudgetMetrics:
    """Tests for retrieving budget metrics."""

    @pytest.mark.asyncio
    async def test_get_budget_metrics(self):
        """Should retrieve budget metrics correctly."""
        with patch("app.core.token_budget.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hgetall = AsyncMock(
                side_effect=[
                    {
                        "tokens_used": "600000",
                        "cost_usd": "1.2",
                        "requests_count": "150",
                    },  # budget_data
                    {
                        "monthly_limit": "1000000",
                        "budget_limit_usd": "2000",
                    },  # config_data
                ]
            )
            mock_redis_factory.return_value = mock_redis

            metrics = await get_budget_metrics("tenant123")

            assert metrics.tenant_id == "tenant123"
            assert metrics.tokens_used_this_month == 600000
            assert metrics.monthly_limit == 1000000
            assert metrics.tokens_remaining == 400000
            assert metrics.usage_percentage == 60.0
            assert metrics.status == BudgetStatus.WARNING  # 60% is in normal range
            assert metrics.requests_today == 150
            assert metrics.avg_tokens_per_request == pytest.approx(4000)

    @pytest.mark.asyncio
    async def test_get_budget_metrics_critical_status(self):
        """Should return CRITICAL status at 90%+ usage."""
        with patch("app.core.token_budget.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hgetall = AsyncMock(
                side_effect=[
                    {"tokens_used": "950000", "cost_usd": "1.9", "requests_count": "200"},
                    {"monthly_limit": "1000000", "budget_limit_usd": "2000"},
                ]
            )
            mock_redis_factory.return_value = mock_redis

            metrics = await get_budget_metrics("tenant123")

            assert metrics.usage_percentage == 95.0
            assert metrics.status == BudgetStatus.CRITICAL

    @pytest.mark.asyncio
    async def test_get_budget_metrics_redis_error(self):
        """Should return default metrics on Redis error."""
        with patch("app.core.token_budget.get_redis") as mock_redis_factory:
            mock_redis = AsyncMock()
            mock_redis.hgetall = AsyncMock(side_effect=Exception("Redis error"))
            mock_redis_factory.return_value = mock_redis

            metrics = await get_budget_metrics("tenant123")

            assert metrics.tokens_used_this_month == 0
            assert metrics.status == BudgetStatus.HEALTHY


class TestBudgetStatus:
    """Tests for budget status calculation."""

    def test_budget_status_healthy(self):
        """Should return HEALTHY when usage is under 70%."""
        status = _get_budget_status(500000, 1000000)
        assert status == BudgetStatus.HEALTHY

    def test_budget_status_warning(self):
        """Should return WARNING when usage is 70-90%."""
        status = _get_budget_status(800000, 1000000)
        assert status == BudgetStatus.WARNING

    def test_budget_status_critical(self):
        """Should return CRITICAL when usage is 90-100%."""
        status = _get_budget_status(950000, 1000000)
        assert status == BudgetStatus.CRITICAL

    def test_budget_status_exceeded(self):
        """Should return EXCEEDED when usage exceeds limit."""
        status = _get_budget_status(1100000, 1000000)
        assert status == BudgetStatus.EXCEEDED

    def test_budget_status_zero_limit(self):
        """Should return HEALTHY for zero limit (unlimited)."""
        status = _get_budget_status(1000000, 0)
        assert status == BudgetStatus.HEALTHY
