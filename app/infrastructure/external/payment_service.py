import os
import stripe
from app.infrastructure.logger import app_logger

# Stripe test payment methods (ver https://docs.stripe.com/testing)
STRIPE_TEST_PM = "pm_card_visa"  # 4242 4242 4242 4242 — siempre approved


class StripePaymentService:
    def __init__(self):
        self.api_key = os.environ.get("STRIPE_API_KEY", "sk_test_mock_key")
        stripe.api_key = self.api_key
        self._simulated = self.api_key == "sk_test_mock_key"

    def create_and_confirm_payment(self, amount_cents: int, metadata: dict = None) -> dict:
        """
        Crea un PaymentIntent y lo confirma inmediatamente con la tarjeta
        de prueba de Stripe (4242 4242 4242 4242).
        Devuelve {intent_id, status, amount_cents}.
        """
        if self._simulated:
            import uuid
            fake_id = f"pi_simulated_{uuid.uuid4().hex[:16]}"
            app_logger.info({"event": "stripe_simulated", "intent_id": fake_id})
            return {"intent_id": fake_id, "status": "succeeded", "amount_cents": amount_cents}

        try:
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="usd",
                payment_method=STRIPE_TEST_PM,
                confirm=True,
                metadata=metadata or {},
            )
            app_logger.info({"event": "stripe_payment_confirmed",
                             "intent_id": intent.id, "status": intent.status})
            if intent.status != "succeeded":
                raise ValueError(f"Pago no procesado. Estado: {intent.status}")
            return {"intent_id": intent.id, "status": intent.status, "amount_cents": amount_cents}
        except stripe.error.CardError as e:
            app_logger.warning({"event": "stripe_card_declined", "code": e.code})
            raise ValueError(f"Tarjeta rechazada: {e.user_message}")
        except stripe.error.StripeError as e:
            app_logger.error({"event": "stripe_error", "details": str(e)})
            raise ValueError(f"Error al procesar el pago: {str(e)}")

    def refund_payment(self, stripe_intent_id: str) -> dict:
        if self._simulated or stripe_intent_id.startswith("pi_simulated_"):
            app_logger.info({"event": "stripe_refund_simulated", "intent_id": stripe_intent_id})
            return {"status": "succeeded", "refund_id": f"re_simulated_{stripe_intent_id[-8:]}"}
        try:
            refund = stripe.Refund.create(payment_intent=stripe_intent_id)
            app_logger.info({"event": "stripe_refunded", "refund_id": refund.id})
            return {"status": refund.status, "refund_id": refund.id}
        except stripe.error.StripeError as e:
            app_logger.error({"event": "stripe_refund_error", "details": str(e)})
            raise ValueError(f"Error al procesar el reembolso: {str(e)}")
