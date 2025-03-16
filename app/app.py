from flask import Flask, request, jsonify
import time
import logging
import json
from opentelemetry import trace, metrics
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.google.cloud.trace import CloudTraceSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.google.cloud.monitoring import CloudMonitoringMetricsExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Configurar rastreamento (Tracing)
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
trace_exporter = CloudTraceSpanExporter()
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(trace_exporter))

# Configurar métricas (Metrics)
metric_reader = PeriodicExportingMetricReader(CloudMonitoringMetricsExporter(), export_interval_millis=5000)
meter_provider = MeterProvider(metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = meter_provider.get_meter("flask-app")

# Definir métricas
requests_counter = meter.create_counter("http_requests_total", description="Número total de requisições HTTP")
requests_errors_counter = meter.create_counter("http_requests_errors_total", description="Número de erros nas requisições")
request_duration = meter.create_histogram("http_request_duration_seconds", description="Duração das requisições")

# Configurar logs estruturados no Google Cloud Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def record_metrics(response):
    duration = time.time() - request.start_time
    request_duration.record(duration, attributes={"route": request.path, "status_code": response.status_code})
    requests_counter.add(1, attributes={"route": request.path, "status_code": response.status_code})

    if response.status_code >= 400:
        requests_errors_counter.add(1, attributes={"route": request.path, "status_code": response.status_code})

    return response

@app.route('/')
def hello():
    with tracer.start_as_current_span("hello"):
        logger.info(json.dumps({"message": "Endpoint / acessado", "status_code": 200}))
        return "Hello, World!"

@app.route('/error')
def error():
    with tracer.start_as_current_span("error"):
        logger.error(json.dumps({"message": "Erro simulado", "status_code": 500}))
        return jsonify({"error": "Erro interno"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
