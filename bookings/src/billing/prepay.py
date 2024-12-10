import paypalrestsdk
import logging
from billing.paypal_config import configure_paypal

configure_paypal()

def create_payment(amount, return_url, cancel_url):
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": str(amount),
                "currency": "USD"
            },
            "description": "Payment description"
        }],
        "redirect_urls": {
            "https://sandbox.paypal.com": return_url,
            "https://sandbox.paypal.com": cancel_url  
        }
    })


    if payment.create():
        logging.info("Payment created successfully")
        
    
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                logging.info(f"Redirecting user to: {approval_url}")
                return approval_url 
    else:
    
        logging.error(f"Error creating payment: {payment.error}")
        return None


def execute_payment(payment_id, payer_id):
    try:
        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({"payer_id": payer_id}):
            logging.info("Payment executed successfully")
            return payment
        else:
            logging.error(f"Error executing payment: {payment.error}")
            return None

    except Exception as e:
        logging.error(f"Unexpected error executing payment: {str(e)}")
        return None
