import os
import stripe
from app.infrastructure.logger import app_logger

class StripePaymentService:
    def __init__(self):
        # Usar test mode key
        self.api_key = os.environ.get('STRIPE_API_KEY', 'sk_test_mock_key')
        stripe.api_key = self.api_key

    def create_payment_intent(self, amount: int, currency: str = 'usd', metadata: dict = None):
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount, # Amount in cents
                currency=currency,
                metadata=metadata or {},
                payment_method_types=['card']
            )
            app_logger.info({"event": "payment_intent_created", "intent_id": intent.id})
            return {"client_secret": intent.client_secret, "id": intent.id}
        except stripe.error.StripeError as e:
            app_logger.error({"event": "stripe_error", "details": str(e)})
            raise ValueError(f"Error procesando el pago simulado: {str(e)}")

    def refund_payment(self, payment_intent_id: str):
        try:
            refund = stripe.Refund.create(payment_intent=payment_intent_id)
            app_logger.info({"event": "payment_refunded", "refund_id": refund.id})
            return {"status": "success", "refund_id": refund.id}
        except stripe.error.StripeError as e:
            app_logger.error({"event": "stripe_refund_error", "details": str(e)})
            raise ValueError(f"Error procesando el reembolso: {str(e)}")
