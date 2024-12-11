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
            "return_url": "https://s3.eu-west-1.amazonaws.com/capstoneprojectpay.com/payment_success.html",
            "cancel_url": "https://s3.eu-west-1.amazonaws.com/capstoneprojectpay.com/payment_cancel.html"
        }

    })

    if payment.create():
        logging.info("Payment created successfully")
        
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = link.href
                logging.info(f"Redirecting user to: {approval_url}")
                return approval_url
        logging.error("Approval URL not found")
        return None
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