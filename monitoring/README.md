cat > monitoring/README.md << 'EOF'
# Monitoring Stack — EnterpriseRAG-AI

This directory contains configuration for the observability stack:
Prometheus, Grafana, Jaeger, and OpenTelemetry.

## Services and Local Ports

| Service    | Purpose                        | Local URL                        |
|------------|--------------------------------|----------------------------------|
| Jaeger UI  | Distributed trace visualization | http://localhost:16686           |
| Prometheus | Metrics aggregation             | http://localhost:9090            |
| Grafana    | Dashboard visualization         | http://localhost:3000            |
| OTLP gRPC  | OTel collector (Jaeger)         | http://localhost:4317            |

## Starting the Stack

```bash
docker-compose up -d
```

All four services start together. Verify with:

```bash
docker-compose ps
```

## Verifying OpenTelemetry Traces

1. Start the API: `uvicorn app.main:app --reload`
2. Make a request: `curl http://localhost:8000/api/v1/query -d '{"question":"test"}'`
3. Open Jaeger UI at **http://localhost:16686**
4. Select service **enterpriserag-api** from the dropdown
5. Click **Find Traces** — you should see a trace with spans for:
   - `fastapi.request`
   - `redis.get` / `redis.set`
   - `faiss.search`
   - `llm.inference`

If no traces appear, check:
- `OTEL_EXPORTER_OTLP_ENDPOINT` is set correctly in `.env`
- Jaeger container is running (`docker-compose ps`)
- The `opentelemetry-sdk` package is installed (`pip install -r requirements.txt`)

## Grafana Default Login

Username: `admin`  Password: `admin` (change on first login)

Pre-built dashboards are in `monitoring/grafana/dashboards/`.

## Prometheus Targets

Prometheus scrapes the FastAPI `/metrics` endpoint every 15 seconds.
Check scrape health at http://localhost:9090/targets.
EOF