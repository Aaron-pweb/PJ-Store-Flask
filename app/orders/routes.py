from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.orders.models import Cart, CartItem, Order, OrderItem
from app.products.models import Product, ProductVariant
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

@orders_bp.route('/cart/add/<int:product_id>', methods=['GET', 'POST'])
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = 1
    variant_id = None

    if request.method == 'POST':
        quantity = int(request.form.get('quantity', 1))
        variant_id = request.form.get('variant_id')
    
    # Check Variant logic
    if variant_id:
        variant = ProductVariant.query.get(variant_id)
        if not variant or variant.product_id != product.id:
            flash('Invalid product option selected.', 'danger')
            return redirect(url_for('products.detail', id=product_id))
        
        if variant.stock < quantity:
            flash(f'Sorry, only {variant.stock} left for {variant.variant_name}.', 'warning')
            return redirect(url_for('products.detail', id=product_id))
    else:
        # Check main product stock if no variant logic (or fallback)
        # Note: If product has variants, we might enforce selection? For now, optional.
        if product.stock < quantity and not product.variants:
             flash(f'Sorry, only {product.stock} left.', 'warning')
             return redirect(url_for('products.detail', id=product_id))

    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    
    # Check if item exists (with same variant)
    cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id, variant_id=variant_id).first()
    if cart_item:
        cart_item.quantity += quantity
        flash(f'Quantity updated.', 'info')
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity, variant_id=variant_id)
        db.session.add(cart_item)
        flash(f'{product.name} added to cart!', 'success')
    
    db.session.commit()
    return redirect(url_for('orders.view_cart'))

@orders_bp.route('/cart/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    if cart_item.cart.user_id != current_user.id:
        abort(403)
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Item removed from cart.', 'info')
    return redirect(url_for('orders.view_cart'))

@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    if not cart or not cart.items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('products.catalog'))
    
    # Check for address selection
    if request.method == 'POST':
        address_id = request.form.get('address_id')
        if not address_id:
            flash('Please select a shipping address.', 'warning')
            return redirect(url_for('orders.checkout'))
        
        # Verify address belongs to user
        from app.auth.models import Address
        address = Address.query.get(address_id)
        if not address or address.user_id != current_user.id:
            flash('Invalid address selected.', 'danger')
            return redirect(url_for('orders.checkout'))
            
        # Create Order
        total = cart.get_total()
        order = Order(
            user_id=current_user.id, 
            total_amount=total, 
            status='Pending',
            shipping_address_id=address.id
        )
        db.session.add(order)
        db.session.commit() # Commit to get ID
        
        # Move items to OrderItem
        for item in cart.items:
            price = item.product.price
            variant_name = None
            
            if item.variant:
                if item.variant.price_override:
                    price = item.variant.price_override
                variant_name = item.variant.variant_name
                
            order_item = OrderItem(
                order_id=order.id, 
                product_id=item.product.id, 
                quantity=item.quantity, 
                price_at_purchase=price,
                variant_name=variant_name,
                variant_id=item.variant_id
            )
            db.session.add(order_item)
        
        # NOTE: WE DO NOT DELETE CART HERE.
        # Cart is cleared only after successful payment or via webhook.
        # If we delete here, a failed payment means the cart is lost.
        
        db.session.commit()
        
        db.session.commit()
        
        flash('Order created! Please proceed to payment.', 'success')
        return redirect(url_for('payments.pay', order_id=order.id))
        
    # GET: Show address selection
    user_addresses = current_user.addresses
    return render_template('orders/checkout_address.html', addresses=user_addresses, cart=cart)
