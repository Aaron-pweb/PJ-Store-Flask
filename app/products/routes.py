from flask import render_template, redirect, url_for, flash, abort, request
from app.products import products_bp
from app.products import products_bp
from app.products.models import Product, Category, ProductVariant
from app.products.forms import ProductForm, VariantForm
from flask_login import login_required, current_user
from app.auth.decorators import seller_required
from app.extensions import db

@products_bp.route("/products")
def catalog():
    query = request.args.get('q')
    category_filter = request.args.get('category')
    
    products_query = Product.query.filter(Product.stock > 0)
    
    if query:
        products_query = products_query.filter(
            (Product.name.ilike(f'%{query}%')) | 
            (Product.description.ilike(f'%{query}%'))
        )
    
    if category_filter:
        products_query = products_query.filter(Product.category == category_filter)
        
    products = products_query.all()
    
    # Get categories for sidebar
    # Optimization: Query Category model directly instead of scanning Products table
    categories = [c[0] for c in Category.query.with_entities(Category.name).order_by(Category.name).all()]

    return render_template('products/catalog.html', products=products, categories=categories, active_category=category_filter, search_query=query)

@products_bp.route("/products/<int:id>")
def detail(id):
    product = Product.query.get_or_404(id)
    return render_template('products/detail.html', product=product)

from app.products.utils import save_picture

@products_bp.route("/products/add", methods=["GET", "POST"])
@login_required
@seller_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        image_file = 'default.jpg'
        if form.image.data:
            image_file = save_picture(form.image.data)
            
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            category=form.category.data,
            image_file=image_file,
            seller_id=current_user.id
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added!', 'success')
        return redirect(url_for('products.my_products'))
    return render_template('products/product_form.html', form=form, title="Add Product")

@products_bp.route("/products/my")
@login_required
@seller_required
def my_products():
    products = Product.query.filter_by(seller_id=current_user.id).all()
    return render_template('products/my_products.html', products=products)

@products_bp.route("/products/edit/<int:id>", methods=["GET", "POST"])
@login_required
@seller_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if product.seller_id != current_user.id:
        abort(403)
    form = ProductForm()
    if form.validate_on_submit():
        if form.image.data:
            product.image_file = save_picture(form.image.data)
            
        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.category = form.category.data
        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('products.my_products'))
    elif request.method == 'GET':
        form.name.data = product.name
        form.description.data = product.description
        form.price.data = product.price
        form.stock.data = product.stock
        form.category.data = product.category
    return render_template('products/product_form.html', form=form, title="Edit Product")

@products_bp.route("/products/delete/<int:id>", methods=["POST"])
@login_required
@seller_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    if product.seller_id != current_user.id:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted!', 'success')
    return redirect(url_for('products.my_products'))
