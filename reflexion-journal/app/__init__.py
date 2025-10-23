from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_login import LoginManager
from .models.models import db, User

migrate = Migrate()
login_manager = LoginManager()

from app.routes.main import main as main_blueprint
from app.routes.auth import auth as auth_blueprint
from app.routes.journal import journal as journal_blueprint
from app.routes.settings import settings as settings_blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(journal_blueprint)
    app.register_blueprint(settings_blueprint, url_prefix='/journal')
    
    return app