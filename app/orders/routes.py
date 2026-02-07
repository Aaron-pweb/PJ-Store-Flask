from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.orders.models import Cart, CartItem, Order, OrderItem
from app.products.models import Product
from app.orders import orders_bp

@orders_bp.route('/cart')
@login_required
def view_cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        # Auto-create cart if it doesn't exist
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    return render_template('orders/cart.html', cart=cart)

@orders_bp.route('/cart/add/<int:product_id>')
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    
    if product.stock <= 0:
        flash('Product is out of stock.', 'danger')
        return redirect(url_for('products.catalog'))

    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id).first()
    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=1)
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'{product.name} added to cart!', 'success')
    return redirect(url_for('orders.view_cart'))

@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart or not cart.items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('products.catalog'))
    
    # Create Order
    total = cart.get_total()
    order = Order(user_id=current_user.id, total_amount=total, status='Pending')
    db.session.add(order)
    db.session.commit() # Commit to get ID
    
    # Move items to OrderItem
    for item in cart.items:
        order_item = OrderItem(
            order_id=order.id, 
            product_id=item.product.id, 
            quantity=item.quantity, 
            price_at_purchase=item.product.price
        )
        db.session.add(order_item)
        # Note: We decrease stock AFTER payment success, not at checkout, 
        # but some prefer reserving stock here. For now, sticking to user instruction:
        # "After Payment success (in the callback)... decrease Product.stock."
    
    # Clear Cart items
    for item in cart.items:
        db.session.delete(item)
    
    db.session.commit()
    
    flash('Order created! Please proceed to payment.', 'success')
    return redirect(url_for('payments.payment', order_id=order.id))
