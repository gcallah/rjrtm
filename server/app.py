from flask import Flask
import logging
from server.city_routes import city_bp    # NEW IMPORT

app = Flask(__name__)

app.register_blueprint(city_bp) 


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Server starting…")

app = Flask(__name__)

# Root endpoint for health check
@app.route('/')
def root():
    logger.info("Successful request to '/'")
    return {'status': 'ok', 'service': 'rjrtm-api', 'version': '0.1'}


if __name__ == '__main__':
    app.run(debug=True)
