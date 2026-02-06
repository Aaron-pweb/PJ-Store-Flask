from flask import Flask
from app.extensions import db
from app.auth import auth_bp
from app.products import products_bp
from app.main import main_bp
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = os.getenv("APP_SECRE_KEY", "dev_key")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app
