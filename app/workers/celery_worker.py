import os
from celery import Celery
from celery.signals import worker_ready
from prometheus_client import start_http_server

# Import the metrics module to register all Celery signal handlers
import app.observability.celery_metrics

# Use environment variable for broker URL, defaulting to localhost
BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery = Celery(
    "worker",
    broker=BROKER_URL
)

@worker_ready.connect
def start_prometheus_metrics_server(sender, **kwargs):
    """
    Start the Prometheus HTTP server when the Celery worker node is fully ready.
    Using `worker_ready` ensures the server is started exactly once by the main 
    worker process, completely avoiding duplicate startup attempts and "Address 
    already in use" errors from child worker processes.
    """
    start_http_server(8001)
    print("Prometheus metrics server started on port 8001")

@celery.task
def process_document(doc_id):
    print(f"Processing {doc_id}")

