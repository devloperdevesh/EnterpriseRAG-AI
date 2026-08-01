"""Token budget monitoring and management for enterprise RAG workloads.

Issue #160: Implements tenant-level token budget tracking to control LLM costs
and provide visibility into token consumption across users and API keys.

Tracks token usage per request, enforces budget limits, and provides cost
estimation metrics for enterprise monitoring and billing.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

from app.core.redis_client import get_redis

# Default token costs (can be configured per LLM provider)
DEFAULT_TOKEN_COSTS = {
    "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
    "claude": {"input": 0.008, "output": 0.024},
}

# Budget monitoring configuration
TOKEN_BUDGET_PREFIX = "token_budget"
BUDGET_CHECK_TIMEOUT_SECONDS = 1.0
COST_TRACKING_ENABLED = True


class BudgetStatus(str, Enum):
    """Token budget status for a tenant."""

    HEALTHY = "healthy"  # Under 70% of monthly budget
    WARNING = "warning"  # 70-90% of monthly budget
    CRITICAL = "critical"  # 90-100% of monthly budget
    EXCEEDED = "exceeded"  # Over monthly budget limit


@dataclass
class TokenUsage:
    """Token usage information for a request."""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    model: str
    estimated_cost: float


@dataclass
class BudgetMetrics:
    """Budget metrics for a tenant."""

    tenant_id: str
    monthly_limit: int
    tokens_used_this_month: int
    tokens_remaining: int
    estimated_spend: float
    budget_limit_usd: float
    estimated_spend_usd: float
    usage_percentage: float
    status: BudgetStatus
    requests_today: int
    avg_tokens_per_request: float
    reset_date: str


async def track_token_usage(
    tenant_id: str,
    user_id: str,
    api_key_id: str,
    input_tokens: int,
    output_tokens: int,
    model: str = "gpt-3.5-turbo",
) -> TokenUsage:
    """Track token usage for a request and update budget metrics.

    Args:
        tenant_id: Unique tenant identifier
        user_id: User making the request
        api_key_id: API key used for the request
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: LLM model used

    Returns:
        TokenUsage object with usage details and cost estimation.
    """
    total_tokens = input_tokens + output_tokens

    # Calculate estimated cost
    token_costs = DEFAULT_TOKEN_COSTS.get(model, DEFAULT_TOKEN_COSTS["gpt-3.5-turbo"])
    input_cost = (input_tokens / 1000) * token_costs["input"]
    output_cost = (output_tokens / 1000) * token_costs["output"]
    estimated_cost = input_cost + output_cost

    usage = TokenUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        model=model,
        estimated_cost=estimated_cost,
    )

    # Update budget metrics in Redis (best-effort, non-blocking)
    try:
        await asyncio.wait_for(
            _update_budget_metrics(tenant_id, user_id, api_key_id, usage),
            timeout=BUDGET_CHECK_TIMEOUT_SECONDS,
        )
    except (asyncio.TimeoutError, Exception):
        # Non-blocking: budget tracking errors don't interrupt queries
        pass

    return usage


async def check_budget_limit(
    tenant_id: str,
    estimated_tokens: int = 0,
) -> tuple[bool, BudgetStatus]:
    """Check if tenant is within budget limits.

    Args:
        tenant_id: Unique tenant identifier
        estimated_tokens: Estimated tokens for the next request

    Returns:
        Tuple of (is_within_budget, budget_status)
    """
    redis_client = get_redis()

    try:
        budget_key = f"{TOKEN_BUDGET_PREFIX}:tenant:{tenant_id}:monthly"
        config_key = f"{TOKEN_BUDGET_PREFIX}:config:{tenant_id}"

        # Get current usage and limits
        budget_data = await asyncio.wait_for(
            redis_client.hgetall(budget_key),
            timeout=BUDGET_CHECK_TIMEOUT_SECONDS,
        )

        config_data = await asyncio.wait_for(
            redis_client.hgetall(config_key),
            timeout=BUDGET_CHECK_TIMEOUT_SECONDS,
        )

        tokens_used = int(budget_data.get("tokens_used", 0))
        monthly_limit = int(config_data.get("monthly_limit", 1000000))

        # Check with estimated future tokens
        projected_usage = tokens_used + estimated_tokens
        status = _get_budget_status(projected_usage, monthly_limit)

        is_within_budget = status != BudgetStatus.EXCEEDED

        return is_within_budget, status

    except asyncio.TimeoutError:
        # Timeout: assume budget is OK to avoid blocking queries
        return True, BudgetStatus.HEALTHY
    except Exception:
        # Error: assume budget is OK for graceful degradation
        return True, BudgetStatus.HEALTHY


async def set_tenant_budget(
    tenant_id: str,
    monthly_limit: int,
    budget_limit_usd: Optional[float] = None,
) -> bool:
    """Configure budget limits for a tenant.

    Args:
        tenant_id: Unique tenant identifier
        monthly_limit: Monthly token limit
        budget_limit_usd: USD budget limit (optional)

    Returns:
        True if successfully set, False otherwise.
    """
    redis_client = get_redis()

    try:
        config_key = f"{TOKEN_BUDGET_PREFIX}:config:{tenant_id}"
        config_data = {
            "monthly_limit": str(monthly_limit),
            "budget_limit_usd": str(budget_limit_usd or 0),
            "configured_at": str(datetime.now(timezone.utc).isoformat()),
        }

        await asyncio.wait_for(
            redis_client.hset(config_key, mapping=config_data),
            timeout=1.0,
        )

        # Set expiry to 1 year (365 days)
        await asyncio.wait_for(
            redis_client.expire(config_key, 365 * 24 * 3600),
            timeout=1.0,
        )

        return True

    except Exception:
        return False


async def get_budget_metrics(tenant_id: str) -> BudgetMetrics:
    """Get current budget metrics for a tenant.

    Args:
        tenant_id: Unique tenant identifier

    Returns:
        BudgetMetrics object with current usage and projections.
    """
    redis_client = get_redis()

    try:
        budget_key = f"{TOKEN_BUDGET_PREFIX}:tenant:{tenant_id}:monthly"
        config_key = f"{TOKEN_BUDGET_PREFIX}:config:{tenant_id}"

        budget_data = await asyncio.wait_for(
            redis_client.hgetall(budget_key),
            timeout=BUDGET_CHECK_TIMEOUT_SECONDS,
        )

        config_data = await asyncio.wait_for(
            redis_client.hgetall(config_key),
            timeout=BUDGET_CHECK_TIMEOUT_SECONDS,
        )

        tokens_used = int(budget_data.get("tokens_used", 0))
        monthly_limit = int(config_data.get("monthly_limit", 1000000))
        budget_limit_usd = float(config_data.get("budget_limit_usd", 1000))
        requests_count = int(budget_data.get("requests_count", 0))

        tokens_remaining = max(0, monthly_limit - tokens_used)
        usage_percentage = (tokens_used / monthly_limit * 100) if monthly_limit > 0 else 0
        avg_tokens = tokens_used / requests_count if requests_count > 0 else 0

        # Estimate USD spend based on GPT-3.5 pricing
        estimated_spend_usd = (tokens_used / 1000) * 0.0015

        status = _get_budget_status(tokens_used, monthly_limit)

        # Calculate reset date (first day of next month)
        now = datetime.now(timezone.utc)
        reset_date = (
            (now.replace(day=1) + timedelta(days=32)).replace(day=1).date().isoformat()
        )

        return BudgetMetrics(
            tenant_id=tenant_id,
            monthly_limit=monthly_limit,
            tokens_used_this_month=tokens_used,
            tokens_remaining=tokens_remaining,
            estimated_spend=tokens_used,
            budget_limit_usd=budget_limit_usd,
            estimated_spend_usd=estimated_spend_usd,
            usage_percentage=usage_percentage,
            status=status,
            requests_today=requests_count,
            avg_tokens_per_request=avg_tokens,
            reset_date=reset_date,
        )

    except Exception:
        # Return default metrics on error
        return BudgetMetrics(
            tenant_id=tenant_id,
            monthly_limit=1000000,
            tokens_used_this_month=0,
            tokens_remaining=1000000,
            estimated_spend=0,
            budget_limit_usd=1000,
            estimated_spend_usd=0,
            usage_percentage=0,
            status=BudgetStatus.HEALTHY,
            requests_today=0,
            avg_tokens_per_request=0,
            reset_date=datetime.now(timezone.utc).replace(day=1).date().isoformat(),
        )


async def _update_budget_metrics(
    tenant_id: str,
    user_id: str,
    api_key_id: str,
    usage: TokenUsage,
) -> None:
    """Internal: Update budget tracking metrics in Redis."""
    redis_client = get_redis()

    budget_key = f"{TOKEN_BUDGET_PREFIX}:tenant:{tenant_id}:monthly"
    user_key = f"{TOKEN_BUDGET_PREFIX}:user:{user_id}:monthly"
    api_key_key = f"{TOKEN_BUDGET_PREFIX}:apikey:{api_key_id}:monthly"

    # Update tenant-level metrics
    await redis_client.hincrby(budget_key, "tokens_used", usage.total_tokens)
    await redis_client.hincrbyfloat(budget_key, "cost_usd", usage.estimated_cost)
    await redis_client.hincrby(budget_key, "requests_count", 1)

    # Update user-level metrics
    await redis_client.hincrby(user_key, "tokens_used", usage.total_tokens)
    await redis_client.hincrbyfloat(user_key, "cost_usd", usage.estimated_cost)
    await redis_client.hincrby(user_key, "requests_count", 1)

    # Update API key-level metrics
    await redis_client.hincrby(api_key_key, "tokens_used", usage.total_tokens)
    await redis_client.hincrbyfloat(api_key_key, "cost_usd", usage.estimated_cost)
    await redis_client.hincrby(api_key_key, "requests_count", 1)

    # Set expiry to 31 days (to track full month)
    for key in [budget_key, user_key, api_key_key]:
        await redis_client.expire(key, 31 * 24 * 3600)


def _get_budget_status(tokens_used: int, monthly_limit: int) -> BudgetStatus:
    """Determine budget status based on usage percentage."""
    if monthly_limit == 0:
        return BudgetStatus.HEALTHY

    usage_percentage = (tokens_used / monthly_limit) * 100

    if usage_percentage >= 100:
        return BudgetStatus.EXCEEDED
    elif usage_percentage >= 90:
        return BudgetStatus.CRITICAL
    elif usage_percentage >= 70:
        return BudgetStatus.WARNING
    else:
        return BudgetStatus.HEALTHY
