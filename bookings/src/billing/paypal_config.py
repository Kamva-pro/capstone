import paypalrestsdk
import logging
from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.getenv('PAYPAL_CLIENT_ID')
client_secret = os.getenv('PAYPAL_CLIENT_SECRET')

paypalrestsdk.configure({
    "mode": "sandbox", 
    "client_id": client_id,
    "client_secret": client_secret
})
logging.basicConfig(level=logging.INFO)