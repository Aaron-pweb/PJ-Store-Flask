from flask import render_template
from app.products import products_bp

@products_bp.route("/products")
def catalog():
    from app.products.models import Product
    products = Product.query.filter(Product.stock > 0).all()
    # If no products, we can pass empty list.
    return render_template('products/catalog.html', products=products)

@products_bp.route("/products/<int:id>")
def detail(id):
    return render_template('products/detail.html', id=id)
