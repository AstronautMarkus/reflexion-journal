from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from .models.models import db

migrate = Migrate()

from app.routes.main import main as main_blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)


    app.register_blueprint(main_blueprint)
    
    return app