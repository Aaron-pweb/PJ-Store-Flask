from flask import render_template
from app.products import products_bp

@products_bp.route("/products")
def catalog():
    return render_template('products/catalog.html')

@products_bp.route("/products/<int:id>")
def detail(id):
    return render_template('products/detail.html', id=id)
