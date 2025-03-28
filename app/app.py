import logging
from flask import Flask
import sys

app = Flask(__name__)

# Configuração do logging para a aplicação
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Remove os handlers padrão do Flask
app.logger.handlers.clear()

# Adiciona o handler personalizado
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Desabilitar log de requisições HTTP do Flask (werkzeug)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Rota principal
@app.route('/')
def hello_world():
    app.logger.info('Requisição recebida na rota /')
    return 'Hello, World!'

# Rota de health check
@app.route('/healthz')
def health_check():
    app.logger.info('Requisição recebida na rota /healthz')
    return 'OK', 200

# Rota simulando um erro
@app.route('/error')
def trigger_error():
    app.logger.error('Erro na rota /error')
    return 'Erro interno do servidor', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
