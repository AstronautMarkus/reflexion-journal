from flask import Flask
from flask_cors import CORS

from app.routes.main import main as main_blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    CORS(app)

    app.register_blueprint(main_blueprint)
    
    return app