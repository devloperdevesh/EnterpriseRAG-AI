from celery import Celery

celery = Celery(
    "worker",
    broker="redis://localhost:6379/0"
)

@celery.task
def process_document(doc_id):
    print(f"Processing {doc_id}")