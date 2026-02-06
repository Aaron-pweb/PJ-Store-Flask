from flask import render_template
from app.products import products_bp

@products_bp.route("/")
def index():
    return "Products Page"
