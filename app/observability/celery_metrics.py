import time
from celery.signals import (
    task_prerun,
    task_postrun,
    task_success,
    task_failure,
    task_retry
)
from prometheus_client import Counter, Histogram, Gauge

# ==============================================================================
# Metric Definitions
# ==============================================================================

CELERY_TASK_STARTED_TOTAL = Counter(
    "celery_task_started_total",
    "Total number of times a Celery task was started",
    ["task_name"]
)

CELERY_TASK_SUCCESS_TOTAL = Counter(
    "celery_task_success_total",
    "Total number of times a Celery task succeeded",
    ["task_name"]
)

CELERY_TASK_FAILURE_TOTAL = Counter(
    "celery_task_failure_total",
    "Total number of times a Celery task failed",
    ["task_name", "exception"]
)

CELERY_TASK_RETRY_TOTAL = Counter(
    "celery_task_retry_total",
    "Total number of times a Celery task was retried",
    ["task_name"]
)

CELERY_TASK_DURATION_SECONDS = Histogram(
    "celery_task_duration_seconds",
    "Time taken to execute a Celery task in seconds",
    ["task_name"]
)

CELERY_ACTIVE_TASKS = Gauge(
    "celery_active_tasks",
    "Number of Celery tasks currently being executed",
    ["task_name"]
)

# Dictionary to store start time of tasks to compute duration
_task_start_times = {}

# ==============================================================================
# Helper Methods
# ==============================================================================

def _get_task_name(task):
    """Safely extract the task name."""
    return task.name if hasattr(task, "name") else "unknown"

# ==============================================================================
# Celery Signal Handlers
# ==============================================================================

@task_prerun.connect
def on_task_prerun(sender, task_id, task, **kwargs):
    """Signal fired before a task starts executing."""
    task_name = _get_task_name(task)
    CELERY_TASK_STARTED_TOTAL.labels(task_name=task_name).inc()
    CELERY_ACTIVE_TASKS.labels(task_name=task_name).inc()
    _task_start_times[task_id] = time.perf_counter()

@task_postrun.connect
def on_task_postrun(sender, task_id, task, **kwargs):
    """Signal fired after a task executes (regardless of success or failure)."""
    start_time = _task_start_times.pop(task_id, None)
    
    # Only decrement and observe if we have a matching start record
    if start_time is not None:
        task_name = _get_task_name(task)
        CELERY_ACTIVE_TASKS.labels(task_name=task_name).dec()
        duration = time.perf_counter() - start_time
        CELERY_TASK_DURATION_SECONDS.labels(task_name=task_name).observe(duration)

@task_success.connect
def on_task_success(sender, **kwargs):
    """Signal fired when a task completes successfully."""
    CELERY_TASK_SUCCESS_TOTAL.labels(task_name=_get_task_name(sender)).inc()

@task_failure.connect
def on_task_failure(sender, exception, **kwargs):
    """Signal fired when a task raises an exception."""
    exception_name = type(exception).__name__
    CELERY_TASK_FAILURE_TOTAL.labels(
        task_name=_get_task_name(sender), 
        exception=exception_name
    ).inc()

@task_retry.connect
def on_task_retry(sender, **kwargs):
    """Signal fired when a task is retried."""
    CELERY_TASK_RETRY_TOTAL.labels(task_name=_get_task_name(sender)).inc()
