from celery import Celery

from opentelemetry import trace
from opentelemetry.propagate import extract

tracer = trace.get_tracer(__name__)

celery = Celery(
    "worker",
    broker="redis://localhost:6379/0"
)


@celery.task(bind=True)
def process_document(
    self,
    doc_id
):

    # =========================
    # Extract propagated trace context
    # =========================

    ctx = extract(self.request.headers)

    # =========================
    # Continue parent trace
    # =========================

    with tracer.start_as_current_span(
        "process-document",
        context=ctx
    ) as span:

        span.set_attribute(
            "document.id",
            str(doc_id)
        )

        print(f"Processing document {doc_id}")

        # Simulated processing
        return {
            "status": "processed",
            "doc_id": doc_id
        }