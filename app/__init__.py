from flask import Flask
from app.extensions import db
from app.auth import auth_bp
from app.products import products_bp
from app.main import main_bp
from app.payments import payments_bp
from app.orders import orders_bp
from app.support import support_bp
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = os.getenv("APP_SECRET_KEY", "dev_key")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    
    from app.extensions import login_manager, csrf
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'

    from app.auth.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from datetime import datetime
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    from app.orders.models import Cart
    from flask_login import current_user
    
    @app.context_processor
    def inject_cart_count():
        count = 0
        if current_user.is_authenticated:
            cart = Cart.query.filter_by(user_id=current_user.id).first()
            if cart and cart.items:
                count = sum(item.quantity for item in cart.items)
        return {'cart_item_count': count}

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(support_bp)

    with app.app_context():
        db.create_all()

    return app
