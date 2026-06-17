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
    password = db.Column(db.String, nullable=True)
    google_id = db.Column(db.String(100), nullable=True, unique=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=True)
    zip_code = db.Column(db.String(20), nullable=True)
    country = db.Column(db.String(100), nullable=False, default='Tanzania')
    is_default = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='addresses')

class UserActivityLog(db.Model):
    __tablename__ = 'user_activity_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action_type = db.Column(db.String(50), nullable=False) # e.g. VIEWED_PRODUCT, SEARCHED, LOGIN
    entity_type = db.Column(db.String(50), nullable=True) # e.g. Product, Address
    entity_id = db.Column(db.Integer, nullable=True)
    metadata_json = db.Column(db.Text, nullable=True) # JSON string for additional details
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('activity_logs', lazy='dynamic'))