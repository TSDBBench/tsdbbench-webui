from flask import Flask
from config import config
from flask_session import Session

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    Session(app)
    config[config_name].init_app(app)
    # attach routes and custom error pages here

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app