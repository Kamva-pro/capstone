import paypalrestsdk
import logging

def configure_paypal():
    paypalrestsdk.configure({
        "mode": "sandbox",
        "client_id": "AT_ljLifWOMRTsuRI82LsEpKB5EAuwnlfb6mOjtCsO9zGl6_hQ469fD806CZRQr3syiUxmxQCzjokMzm",
        "client_secret": "EMnfYn2SIawcY_a8MivhtM3PKuhtjGCdnn9vy7d7CcTWdhlUS3zOGmAfsbVHt9Ish_XMX07OeoMvpLrb"
    })
    logging.basicConfig(level=logging.INFO)