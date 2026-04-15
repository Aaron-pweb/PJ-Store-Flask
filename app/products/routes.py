from flask import render_template, redirect, url_for, flash, abort, request
from app.products import products_bp
from app.products import products_bp
from app.products.models import Product, Category, ProductVariant, Review, Wishlist
from app.products.forms import ProductForm, VariantForm, CategoryForm, ReviewForm
from app.orders.models import OrderItem, Order
from flask_login import login_required, current_user
from app.auth.decorators import seller_required, admin_required
from app.extensions import db

@products_bp.route("/products")
def catalog():
    query = request.args.get('q')
    category_filter = request.args.get('category')
    
    products_query = Product.query.filter(Product.stock > 0, Product.is_active == True)
    
    if query:
        search_terms = query.split()
        for term in search_terms:
            products_query = products_query.filter(
                (Product.name.ilike(f'%{term}%')) | 
                (Product.description.ilike(f'%{term}%'))
            )
    
    if category_filter:
        products_query = products_query.filter(Product.category == category_filter)
        
    sort = request.args.get('sort')
    if sort == 'price_asc':
        products_query = products_query.order_by(Product.price.asc())
    elif sort == 'price_desc':
        products_query = products_query.order_by(Product.price.desc())
    elif sort == 'newest':
        products_query = products_query.order_by(Product.id.desc())
    else:
        products_query = products_query.order_by(Product.id.desc()) # Default newest

    page = request.args.get('page', 1, type=int)
    products_pagination = products_query.paginate(page=page, per_page=12)
    products = products_pagination.items
    
    # Get categories for sidebar
    # Optimization: Query Category model directly instead of scanning Products table
    categories = [c[0] for c in Category.query.with_entities(Category.name).order_by(Category.name).all()]

    return render_template('products/catalog.html', products=products, pagination=products_pagination, categories=categories, active_category=category_filter, search_query=query, current_sort=sort)

@products_bp.route("/products/<int:id>")
def detail(id):
    product = Product.query.get_or_404(id)
    reviews = Review.query.filter_by(product_id=id).order_by(Review.created_at.desc()).all()
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0

    in_wishlist = False
    can_review = False

    if current_user.is_authenticated:
        in_wishlist = Wishlist.query.filter_by(user_id=current_user.id, product_id=id).first() is not None

        # Check if user has a delivered order for this product and hasn't reviewed it yet
        purchased_item = OrderItem.query.join(Order).filter(
            Order.user_id == current_user.id,
            Order.status == 'Delivered',
            OrderItem.product_id == id
        ).first()

        if purchased_item:
            existing_review = Review.query.filter_by(user_id=current_user.id, order_item_id=purchased_item.id).first()
            if not existing_review:
                can_review = True

    return render_template('products/detail.html', product=product, reviews=reviews, avg_rating=avg_rating, in_wishlist=in_wishlist, can_review=can_review)

@products_bp.route("/products/<int:id>/review", methods=["GET", "POST"])
@login_required
def add_review(id):
    product = Product.query.get_or_404(id)

    # Strictly check if user purchased and received the product
    purchased_item = OrderItem.query.join(Order).filter(
        Order.user_id == current_user.id,
        Order.status == 'Delivered',
        OrderItem.product_id == id
    ).first()

    if not purchased_item:
        flash("You can only review products you have purchased and received.", "danger")
        return redirect(url_for('products.detail', id=id))

    existing_review = Review.query.filter_by(user_id=current_user.id, order_item_id=purchased_item.id).first()
    if existing_review:
        flash("You have already reviewed this purchase.", "warning")
        return redirect(url_for('products.detail', id=id))

    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            user_id=current_user.id,
            product_id=product.id,
            order_item_id=purchased_item.id,
            rating=form.rating.data,
            title=form.title.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        flash("Thank you for your review!", "success")
        return redirect(url_for('products.detail', id=id))

    return render_template('products/review_form.html', form=form, product=product)

@products_bp.route("/wishlist")
@login_required
def wishlist():
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('products/wishlist.html', items=wishlist_items)

@products_bp.route("/products/<int:id>/wishlist/toggle", methods=["POST"])
@login_required
def toggle_wishlist(id):
    product = Product.query.get_or_404(id)
    item = Wishlist.query.filter_by(user_id=current_user.id, product_id=id).first()

    if item:
        db.session.delete(item)
        flash(f"{product.name} removed from wishlist.", "success")
    else:
        new_item = Wishlist(user_id=current_user.id, product_id=id)
        db.session.add(new_item)
        flash(f"{product.name} added to wishlist.", "success")

    db.session.commit()
    return redirect(request.referrer or url_for('products.detail', id=id))

from app.products.utils import save_picture

@products_bp.route("/category/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data, slug=form.slug.data)
        db.session.add(category)
        db.session.commit()
        flash('Category added!', 'success')
        return redirect(url_for('products.add_product'))
    return render_template('products/category_form.html', form=form, title="Add Category")

@products_bp.route("/products/add", methods=["GET", "POST"])
@login_required
@seller_required
def add_product():
    categories = Category.query.all()
    if not categories:
        flash("No categories found. Please ask an administrator to add categories first.", "warning")

    form = ProductForm()
    # Populate category choices dynamically
    form.category.choices = [(c.name, c.name) for c in categories]
    
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
    active_products = Product.query.filter_by(seller_id=current_user.id, is_active=True).all()
    archived_products = Product.query.filter_by(seller_id=current_user.id, is_active=False).all()
    return render_template('products/my_products.html', products=active_products, archived_products=archived_products)

@products_bp.route("/products/edit/<int:id>", methods=["GET", "POST"])
@login_required
@seller_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    if product.seller_id != current_user.id:
        abort(403)
    
    categories = Category.query.all()
    form = ProductForm()
    # Populate category choices dynamically
    form.category.choices = [(c.name, c.name) for c in categories]
    
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
    product.is_active = False
    db.session.commit()
    flash('Product archived.', 'success')
    return redirect(url_for('products.my_products'))

@products_bp.route("/products/restore/<int:id>", methods=["POST"])
@login_required
@seller_required
def restore_product(id):
    product = Product.query.get_or_404(id)
    if product.seller_id != current_user.id:
        abort(403)
    product.is_active = True
    db.session.commit()
    flash('Product restored!', 'success')
    return redirect(url_for('products.my_products'))

@products_bp.route("/products/<int:id>/variants", methods=["GET", "POST"])
@login_required
@seller_required
def manage_variants(id):
    product = Product.query.get_or_404(id)
    if product.seller_id != current_user.id:
        abort(403)
        
    form = VariantForm()
    if form.validate_on_submit():
        variant = ProductVariant(
            product_id=product.id,
            variant_name=form.variant_name.data,
            stock=form.stock.data,
            price_override=form.price_override.data
        )
        db.session.add(variant)
        db.session.commit()
        flash('Variant added!', 'success')
        return redirect(url_for('products.manage_variants', id=id))
        
    return render_template('products/manage_variants.html', product=product, form=form)

@products_bp.route("/products/variants/delete/<int:id>", methods=["POST"])
@login_required
@seller_required
def delete_variant(id):
    variant = ProductVariant.query.get_or_404(id)
    product = Product.query.get(variant.product_id)
    if product.seller_id != current_user.id:
        abort(403)
        
    db.session.delete(variant)
    db.session.commit()
    flash('Variant deleted.', 'success')
    return redirect(url_for('products.manage_variants', id=product.id))
