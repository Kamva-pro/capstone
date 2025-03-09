import paypalrestsdk
import logging
from billing.paypal_config import configure_paypal

configure_paypal()

def setup_recurring_payment(plan):
    try:
        billing_plan = paypalrestsdk.BillingPlan.find(plan)

        if billing_plan:
            logging.info("Billing plan found successfully")
            return billing_plan
        else:
            logging.error(f"Billing plan with ID {plan} not found")
            return None

    except paypalrestsdk.exceptions.PayPalConnectionError as e:
        logging.error(f"Error connecting to PayPal: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return None