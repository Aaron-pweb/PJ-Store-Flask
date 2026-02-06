from flask import Blueprint

main_bp = Blueprint('main', __name__, url_prefix="/", template_folder='templates')

from app.main import routes
