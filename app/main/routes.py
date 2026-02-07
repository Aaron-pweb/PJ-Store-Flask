from flask import render_template
from app.main import main_bp

@main_bp.route("/")
def index():
    return render_template('main/index.html', home="home")

from app.auth.decorators import admin_required
@main_bp.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    return "<h1>Admin Dashboard - Restricted Area</h1>"
