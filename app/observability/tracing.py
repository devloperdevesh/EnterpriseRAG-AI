from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

def setup_tracing():

    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({
                SERVICE_NAME: "enterprise-genai-platform"
            })
        )
    )

    tracer = trace.get_tracer(__name__)

    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )

    span_processor = BatchSpanProcessor(jaeger_exporter)

    trace.get_tracer_provider().add_span_processor(
        span_processor
    )

    return tracer