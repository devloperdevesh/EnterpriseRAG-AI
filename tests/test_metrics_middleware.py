from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.middleware import MetricsMiddleware


def test_middleware_runs_without_type_error():
    app = FastAPI()

    @app.get("/ping")
    def ping():
        return {"ok": True}

    app.add_middleware(MetricsMiddleware)
    client = TestClient(app)

    resp = client.get("/ping")
    assert resp.status_code == 200
