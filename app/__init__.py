from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_smorest import Api
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)
    ma.init_app(app)

    from . import models
    with app.app_context():
        db.create_all()

    api = Api(app)

    from .routes import blp 
    api.register_blueprint(blp)

    return app
    