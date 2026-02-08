from flask import Blueprint

payments_bp = Blueprint('payments', __name__, url_prefix='/payments', template_folder='templates')

from app.payments import routes
