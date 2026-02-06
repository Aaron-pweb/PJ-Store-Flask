from flask import render_template, request, redirect, url_for, flash, jsonify
from app.payments import payments_bp
from app.payments.utils import initiate_chapa_payment, verify_chapa_payment
import uuid

@payments_bp.route("/pay", methods=["POST", "GET"])
def pay():
    if request.method == "POST":
        # Example data - in a real app, get this from a cart/order model
        amount = "100"
        email = "customer@example.com" 
        first_name = "Jane"
        last_name = "Doe"
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
