from flask import Flask
from .config import Config  # Relative import
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Initialize extensions without binding to the app yet
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Configure Flask-Login
login_manager.login_view = 'main.login'  # Blueprint route for login
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Import and register Blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

app = create_app()
