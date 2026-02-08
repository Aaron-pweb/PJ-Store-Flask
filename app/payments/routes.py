from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.payments import payments_bp
from app.payments.utils import initiate_chapa_payment, verify_chapa_payment
import uuid

from app.extensions import db
from app.orders.models import Order, Cart, CartItem
from app.products.models import Product

@payments_bp.route("/pay/<int:order_id>", methods=["POST", "GET"])
@login_required 
def pay(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Ensure current user owns the order
    if order.user_id != current_user.id:
        flash("Unauthorized access to this order", "danger")
        return redirect(url_for('products.catalog'))
        
    if order.status == 'Paid':
        flash("This order has already been paid.", "info")
        return redirect(url_for('products.catalog'))

    if request.method == "POST" or request.method == "GET": # Auto-redirect for now or show confirmation
        amount = str(order.total_amount)
        email = current_user.email
        first_name = current_user.full_name.split(" ")[0] if " " in current_user.full_name else current_user.full_name
        last_name = current_user.full_name.split(" ")[1] if " " in current_user.full_name else ""
        
        # Generate or reuse tx_ref
        if not order.tx_ref:
            order.tx_ref = str(uuid.uuid4())
            db.session.commit()
            
        tx_ref = order.tx_ref
        
        # Build return URL with tx_ref to verify on return
        return_url = url_for('payments.payment_success', tx_ref=tx_ref, _external=True)

        response = initiate_chapa_payment(amount, email, first_name, last_name, tx_ref, return_url=return_url)
        
        if response.get("status") == "success":
            return redirect(response["data"]["checkout_url"])
        else:
            flash("Error initiating payment", "danger")
            return redirect(url_for('orders.checkout'))
            
    return render_template('payments/pay.html', order=order)

@payments_bp.route("/payment-success")
def payment_success():
    tx_ref = request.args.get('tx_ref')
    if not tx_ref:
        return redirect(url_for('products.catalog'))
        
    order = Order.query.filter_by(tx_ref=tx_ref).first()
    if not order:
        flash("Order not found", "danger")
        return redirect(url_for('products.catalog'))
        
    # Verify payment with Chapa
    verification = verify_chapa_payment(tx_ref)
    
    if verification.get("status") == "success" or verification.get("message") == "Payment details":
        # Check if already marked as paid to avoid double deduction
        if order.status != 'Paid':
            order.status = 'Paid'
            
            # Decrease stock
            for item in order.items:
                product = Product.query.get(item.product_id)
                if product:
                    product.stock -= item.quantity
                    db.session.add(product)
            
            # Clear User's Cart
            cart = Cart.query.filter_by(user_id=order.user_id).first()
            if cart:
                for item in cart.items:
                    db.session.delete(item)
                # potentially delete cart too? no, keep it empty.

            db.session.commit()
            flash("Payment successful!", "success")
    else:
        flash("Payment verification failed", "warning")
        
    return render_template('payments/success.html', order=order)

@payments_bp.route("/callback")
def callback():
    # Handle callback from Chapa
    # In a real production app, this is where you'd reliably handle updates 
    # even if the user closes the browser.
    return "Payment Callback Received"

@payments_bp.route("/webhook", methods=["POST"])
def webhook():
    # Verify signature and update order status
    # data = request.json
    return jsonify({"status": "success"}), 200
