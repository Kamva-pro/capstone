import paypalrestsdk
import logging
from billing.paypal_config import configure_paypal

configure_paypal()

def setup_recurring_payment(plan):
    billing_plan = paypalrestsdk.BillingPlan.find(plan)

    if billing_plan:
        logging.info("Billing plan found successfully")
        return billing_plan
    else:
        logging.error(billing_plan.error)
        return None
