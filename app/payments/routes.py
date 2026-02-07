from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.payments import payments_bp
from app.payments.utils import initiate_chapa_payment, verify_chapa_payment
import uuid

@payments_bp.route("/pay", methods=["POST", "GET"])
@login_required # Secured
def pay()    :
    if request.method == "POST":
        # Example data - in a real app, get this from a cart/order model
        amount = "100"
        email = current_user.email # Use logged in user's email
        first_name = current_user.full_name.split(" ")[0] if " " in current_user.full_name else current_user.full_name
        last_name = current_user.full_name.split(" ")[1] if " " in current_user.full_name else ""
        tx_ref = str(uuid.uuid4()) # Unique transaction reference

        response = initiate_chapa_payment(amount, email, first_name, last_name, tx_ref)
        
        if response.get("status") == "success":
            return redirect(response["data"]["checkout_url"])
        else:
            flash("Error initiating payment", "danger")
            return redirect(url_for('payments.pay'))
            
    return render_template('pay.html') # You'll need to create this template or remove this line

@payments_bp.route("/callback")
def callback():
    # Handle callback from Chapa
    return "Payment Callback Received"

@payments_bp.route("/webhook", methods=["POST"])
def webhook():
    # Verify signature and update order status
    data = request.json
    return jsonify({"status": "success"}), 200
