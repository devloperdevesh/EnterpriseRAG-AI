import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from middleware.middleware import MetricsMiddleware


def test_metrics_middleware_imports_and_runs():
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint():
        return {"ok": True}

    app.add_middleware(MetricsMiddleware)

    client = TestClient(app)
    resp = client.get("/test")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
