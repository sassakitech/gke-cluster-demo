from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
import sys

app = Flask(__name__)

# Configuração do logging
handler = logging.StreamHandler(sys.stdout)  # Envia logs para stdout
handler.setLevel(logging.INFO)  # Define o nível de log como INFO
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Remove os handlers padrão do Flask
app.logger.handlers.clear()

# Adiciona o handler personalizado
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Rota principal
@app.route('/')
def hello_world():
    app.logger.info('Requisição recebida na rota /')  # Log personalizado
    return 'Hello, World!'

# Rota de health check
@app.route('/healthz')
def health_check():
    app.logger.info('Requisição recebida na rota /healthz')  # Log personalizado
    return 'OK', 200

# Rota simulando um erro
@app.route('/error')
def trigger_error():
    try:
        # Simula um erro (divisão por zero)
        result = 1 / 0
    except Exception as e:
        app.logger.error(f'Erro na rota /error: {str(e)}', exc_info=True)  # Log de erro com traceback
        return 'Erro interno do servidor', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
