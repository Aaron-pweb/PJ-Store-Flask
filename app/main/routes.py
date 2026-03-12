from flask import render_template
from app.main import main_bp
from app.products.models import Product, Category

@main_bp.route("/")
def index():
    featured_products = Product.query.filter_by(is_active=True).order_by(Product.id.desc()).limit(4).all()
    categories = Category.query.all()
    return render_template('main/index.html', featured_products=featured_products, categories=categories)

@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@main_bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

