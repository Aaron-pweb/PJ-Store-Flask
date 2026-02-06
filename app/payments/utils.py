import requests
import os

def initiate_chapa_payment(amount, email, first_name, last_name, tx_ref):
    url = "https://api.chapa.co/v1/transaction/initialize"
    payload = {
        "amount": amount,
        "currency": "ETB",
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "tx_ref": tx_ref,
        "callback_url": "https://your-website.com/payments/callback", # Update with actual domain
        "return_url": "https://your-website.com/payments/success",
        "customization[title]": "Payment for Order",
        "customization[description]": "I love paying with Chapa"
    }
    headers = {
        'Authorization': f'Bearer {os.getenv("CHAPA_SECRET_KEY")}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

def verify_chapa_payment(tx_ref):
    url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
    payload = {}
    headers = {
        'Authorization': f'Bearer {os.getenv("CHAPA_SECRET_KEY")}'
    }
    response = requests.get(url, headers=headers, data=payload)
    return response.json()
