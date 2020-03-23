# coding: utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config


db = SQLAlchemy()


# 工厂方法
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from main.api_1_0 import api as api_blueprint
    app.register_blueprint(api_blueprint)

    return app

