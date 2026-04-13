from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
login_manager = LoginManager()
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()
oauth = OAuth()
