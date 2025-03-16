from flask import Flask, request
import logging
import json
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.google.cloud.trace import CloudTraceSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.google.cloud.monitoring import CloudMonitoringMetricsExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk._logs.export import LoggingHandler

# Configuração do OpenTelemetry para traces
trace.set_tracer_provider(TracerProvider(resource=Resource.create({"service.name": "flask-app"})))
cloud_trace_exporter = CloudTraceSpanExporter()
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(cloud_trace_exporter))

# Configuração do OpenTelemetry para métricas
metric_reader = PeriodicExportingMetricReader(
    CloudMonitoringMetricsExporter(), export_interval_millis=5000
)
meter_provider = MeterProvider(metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = meter_provider.get_meter("flask-app")

# Configuração do logging estruturado com OpenTelemetry
class OpenTelemetryLoggingFormatter(logging.Formatter):
    def format(self, record):
        record_dict = {
            "time": self.formatTime(record, self.datefmt),
            "severity": record.levelname,
            "message": record.getMessage(),
        }
        
        span = trace.get_current_span()
        if span:
            record_dict["trace_id"] = format(span.get_span_context().trace_id, '032x')
            record_dict["span_id"] = format(span.get_span_context().span_id, '016x')

        return json.dumps(record_dict)

log_handler = LoggingHandler()
log_handler.setFormatter(OpenTelemetryLoggingFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)  # Instrumentação do Flask com OpenTelemetry

# Métricas personalizadas
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
        requests_counter.add(1, attributes={"route": "/", "status_code": "200"})
        return 'Hello, World!'

@app.route('/healthz')
def health_check():
    with trace.get_tracer(__name__).start_as_current_span("health_check"):
        logger.info('Endpoint /healthz acessado', extra={
            "http.method": request.method,
            "http.route": "/healthz",
            "http.status_code": 200,
       
