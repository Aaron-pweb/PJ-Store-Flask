from flask import Blueprint

support_bp = Blueprint('support', __name__, template_folder='templates')

from app.support import routes
