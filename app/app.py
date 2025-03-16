from flask import Flask, request, jsonify
import logging
import time
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

requests_errors_counter = meter.create_counter(
    "http_requests_errors_total",
    description="Total de requisições HTTP com erro",
    unit="1",
)

request_duration = meter.create_histogram(
    "http_request_duration_seconds",
    description="Duração das requisições HTTP",
    unit="s",
)

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def record_metrics(response):
    duration = time.time() - request.start_time
    request_duration.record(duration, attributes={"route": request.path, "status_code": str(response.status_code)})

    requests_counter.add(1, attributes={"route": request.path, "status_code": str(response.status_code)})

    if response.status_code >= 400:
        requests_errors_counter.add(1, attributes={"route": request.path, "status_code": str(response.status_code)})

    return response

@app.route('/')
def hello_world():
    with trace.get_tracer(__name__).start_as_current_span("hello_world"):
        logger.info('Endpoint / acessado', extra={
            "http.method": request.method,
            "http.route": "/",
            "http.status_code": 200,
        })
        return 'Hello, World!'

@app.route('/healthz')
def health_check():
    with trace.get_tracer(__name__).start_as_current_span("health_check"):
        logger.info('Endpoint /healthz acessado', extra={
            "http.method": request.method,
            "http.route": "/healthz",
            "http.status_code": 200,
        })
        return 'OK', 200

@app.route('/error')
def error_endpoint():
    with trace.get_tracer(__name__).start_as_current_span("error_endpoint"):
        logger.error('Erro simulado', extra={
            "http.method": request.method,
            "http.route": "/error",
            "http.status_code": 500,
        })
        return jsonify({"error": "Erro interno"}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Captura erros não tratados e registra métricas de erro"""
    logger.error(f'Erro inesperado: {str(e)}', extra={
        "http.method": request.method,
        "http.route": request.path,
        "http.status_code": 500,
    })
    requests_errors_counter.add(1, attributes={"route": request.path, "status_code": "500"})
    return jsonify({"error": "Erro interno"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
