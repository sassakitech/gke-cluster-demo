from flask import Flask, request
import logging
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.cloud_monitoring import CloudMonitoringMetricsExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Configuração do OpenTelemetry para traces
trace.set_tracer_provider(TracerProvider(resource=Resource.create({"service.name": "flask-app"})))
cloud_trace_exporter = CloudTraceSpanExporter()
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(cloud_trace_exporter))

# Configuração do OpenTelemetry para métricas
metric_reader = PeriodicExportingMetricReader(
    CloudMonitoringMetricsExporter(), export_interval_millis=5000
)
metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))

# Configuração do logging para logs estruturados
logging.basicConfig(level=logging.INFO, format='{"time": "%(asctime)s", "severity": "%(levelname)s", "message": "%(message)s", "trace_id": "%(otelTraceID)s", "span_id": "%(otelSpanID)s"}')
logger = logging.getLogger(__name__)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)  # Instrumentação do Flask com OpenTelemetry

# Métricas personalizadas
meter = metrics.get_meter("flask-app")
requests_counter = meter.create_counter(
    "http_requests_total",
    description="Total de requisições HTTP",
    unit="1",
)
request_duration = meter.create_histogram(
    "http_request_duration_seconds",
    description="Duração das requisições HTTP",
    unit="s",
)

@app.route('/')
def hello_world():
    with trace.get_tracer(__name__).start_as_current_span("hello_world"):
        logger.info('Endpoint / acessado', extra={
            "http.method": request.method,
            "http.route": "/",
            "http.status_code": 200,
        })
        requests_counter.add(1, {"route": "/", "status_code": 200})
        return 'Hello, World!'

@app.route('/healthz')
def health_check():
    with trace.get_tracer(__name__).start_as_current_span("health_check"):
        logger.info('Endpoint /healthz acessado', extra={
            "http.method": request.method,
            "http.route": "/healthz",
            "http.status_code": 200,
        })
        requests_counter.add(1, {"route": "/healthz", "status_code": 200})
        return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)