from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()
