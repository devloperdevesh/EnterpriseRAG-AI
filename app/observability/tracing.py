from opentelemetry import trace
from opentelemetry.propagate import set_global_textmap

from opentelemetry.sdk.resources import (
    SERVICE_NAME,
    Resource,
)

from opentelemetry.sdk.trace import TracerProvider

from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)

from opentelemetry.exporter.jaeger.thrift import (
    JaegerExporter,
)

from opentelemetry.trace.propagation.tracecontext import (
    TraceContextTextMapPropagator,
)


def setup_tracing():

    resource = Resource.create({
        SERVICE_NAME: "enterprise-genai-platform"
    })

    provider = TracerProvider(
        resource=resource
    )

    trace.set_tracer_provider(provider)

    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )

    span_processor = BatchSpanProcessor(
        jaeger_exporter
    )

    provider.add_span_processor(
        span_processor
    )

    # =========================
    # Enable W3C trace context propagation
    # =========================

    set_global_textmap(
        TraceContextTextMapPropagator()
    )

    return trace.get_tracer(__name__)