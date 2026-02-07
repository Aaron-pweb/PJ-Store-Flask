from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.auth.constants import Roles

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=Roles.CUSTOMER) # super_admin, admin, seller, support, customer
    is_approved = db.Column(db.Boolean, default=True) # False for Sellers until approved
    user_name = db.Column(db.String(150), nullable=False, unique=True)
    age = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)