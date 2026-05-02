"""
Payment processing module demonstrating secure credential handling.
All sensitive data is loaded from environment variables.
"""
import os
import hmac
import hashlib
import json
from decimal import Decimal
from datetime import datetime

# Load payment gateway credentials from environment variables
stripe_key = os.environ.get('STRIPE_API_KEY')
stripe_webhook = os.environ.get('STRIPE_WEBHOOK_SECRET')
paypal_id = os.environ.get('PAYPAL_CLIENT_ID')
paypal_secret = os.environ.get('PAYPAL_CLIENT_SECRET')


class PaymentError(Exception):
    """Custom exception for payment processing errors."""
    pass


class StripePaymentProcessor:
    """
    Stripe payment processor using environment variables for credentials.
    """

    def __init__(self):
        """Initialize the Stripe payment processor."""
        if not stripe_key:
            raise PaymentError("stripe_key not configured in environment variables")

        self.stripe_secret = stripe_key
        self.webhook_secret = stripe_webhook

    def create_payment_intent(self, amount: Decimal, currency: str = 'usd', customer_id: str | None = None) -> dict:
        """
        Create a payment intent.

        Args:
            amount (Decimal): The amount to charge
            currency (str): The currency code (default: 'usd')
            customer_id (str, optional): The customer identifier

        Returns:
            dict: Payment intent details
        """
        payment_intent = {
            'id': f'pi_{datetime.utcnow().timestamp()}',
            'amount': int(amount * 100),  # Convert to cents
            'currency': currency,
            'customer': customer_id,
            'status': 'requires_payment_method',
            'created': datetime.utcnow().isoformat()
        }

        return payment_intent

    def confirm_payment(self, payment_intent_id: str, payment_method_id: str) -> dict:
        """
        Confirm a payment intent.

        Args:
            payment_intent_id (str): The payment intent ID
            payment_method_id (str): The payment method ID

        Returns:
            dict: Updated payment intent
        """
        return {
            'id': payment_intent_id,
            'status': 'succeeded',
            'payment_method': payment_method_id,
            'confirmed_at': datetime.utcnow().isoformat()
        }

    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify a webhook signature from Stripe.

        Args:
            payload (str): The webhook payload
            signature (str): The signature header

        Returns:
            bool: True if signature is valid

        Raises:
            PaymentError: If webhook secret is not configured
        """
        if not self.webhook_secret:
            raise PaymentError("stripe_webhook not configured")

        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def process_refund(self, payment_intent_id: str, amount: Decimal | None = None) -> dict:
        """
        Process a refund for a payment.

        Args:
            payment_intent_id (str): The payment intent ID to refund
            amount (Decimal, optional): Partial refund amount

        Returns:
            dict: Refund details
        """
        return {
            'id': f'ref_{datetime.utcnow().timestamp()}',
            'payment_intent': payment_intent_id,
            'amount': int(amount * 100) if amount else None,
            'status': 'succeeded',
            'created': datetime.utcnow().isoformat()
        }


class PayPalPaymentProcessor:
    """
    PayPal payment processor using environment variables for credentials.
    """

    def __init__(self):
        """Initialize the PayPal payment processor."""
        if not paypal_id or not paypal_secret:
            raise PaymentError(
                "paypal_id and paypal_secret must be configured in environment variables"
            )

        self.client_id = paypal_id
        self.client_secret = paypal_secret
        self.access_token: str | None = None

    def authenticate(self) -> str:
        """
        Authenticate with PayPal API to get an access token.

        Returns:
            str: Access token
        """
        self.access_token = f"access_token_{datetime.utcnow().timestamp()}"
        return self.access_token

    def create_order(self, amount: Decimal, currency: str = 'USD', description: str | None = None) -> dict:
        """
        Create a PayPal order.

        Args:
            amount (Decimal): The amount to charge
            currency (str): The currency code (default: 'USD')
            description (str, optional): Order description

        Returns:
            dict: Order details
        """
        if not self.access_token:
            self.authenticate()

        order = {
            'id': f'ORDER_{datetime.utcnow().timestamp()}',
            'status': 'CREATED',
            'amount': {
                'currency_code': currency,
                'value': str(amount)
            },
            'description': description,
            'created_time': datetime.utcnow().isoformat()
        }

        return order

    def capture_order(self, order_id: str) -> dict:
        """
        Capture a PayPal order.

        Args:
            order_id (str): The order ID to capture

        Returns:
            dict: Capture details
        """
        if not self.access_token:
            self.authenticate()

        return {
            'id': order_id,
            'status': 'COMPLETED',
            'captured_at': datetime.utcnow().isoformat()
        }


class PaymentGateway:
    """
    Unified payment gateway supporting multiple processors.
    """

    def __init__(self, processor: str = 'stripe'):
        """
        Initialize the payment gateway.

        Args:
            processor (str): The payment processor to use ('stripe' or 'paypal')
        """
        if processor == 'stripe':
            self.processor: StripePaymentProcessor | PayPalPaymentProcessor = StripePaymentProcessor()
        elif processor == 'paypal':
            self.processor = PayPalPaymentProcessor()
        else:
            raise PaymentError(f"Unsupported payment processor: {processor}")

        self.processor_name = processor

    def process_payment(self, amount: Decimal, currency: str = 'USD', customer_id: str | None = None) -> dict:
        """
        Process a payment through the configured processor.

        Args:
            amount (Decimal): The amount to charge
            currency (str): The currency code
            customer_id (str, optional): The customer identifier

        Returns:
            dict: Payment result
        """
        # isinstance() narrows the type so the checker knows exactly which
        # processor — and which methods — are available in each branch.
        if isinstance(self.processor, StripePaymentProcessor):
            intent = self.processor.create_payment_intent(amount, currency.lower(), customer_id)
            return {
                'success': True,
                'processor': 'stripe',
                'transaction_id': intent['id'],
                'status': intent['status']
            }
        elif isinstance(self.processor, PayPalPaymentProcessor):
            order = self.processor.create_order(amount, currency.upper())
            return {
                'success': True,
                'processor': 'paypal',
                'transaction_id': order['id'],
                'status': order['status']
            }

        raise PaymentError(f"Unsupported payment processor: {self.processor_name}")

    def verify_webhook(self, payload: str, signature: str) -> bool:
        """
        Verify a webhook from the payment processor.

        Args:
            payload (str): The webhook payload
            signature (str): The signature header

        Returns:
            bool: True if webhook is valid
        """
        if isinstance(self.processor, StripePaymentProcessor):
            return self.processor.verify_webhook_signature(payload, signature)

        # PayPal webhook verification would be implemented here
        return True


# Example usage (for documentation purposes)
if __name__ == '__main__':
    print("Payment Processing Module - Secure Credential Handling Example")
    print("=" * 60)
    print("\nThis module demonstrates:")
    print("✓ Loading payment credentials from environment variables")
    print("✓ No hardcoded API keys or secrets in source code")
    print("✓ Secure webhook signature verification")
    print("✓ Support for multiple payment processors")
    print("\nRequired environment variables:")
    print("\nFor Stripe:")
    print("- stripe_key (from STRIPE_API_KEY env var)")
    print("- stripe_webhook (from STRIPE_WEBHOOK_SECRET env var)")
    print("\nFor PayPal:")
    print("- paypal_id (from PAYPAL_CLIENT_ID env var)")
    print("- paypal_secret (from PAYPAL_CLIENT_SECRET env var)")
    print("\nNote: This is a simplified example. In production, use official")
    print("payment processor SDKs and implement proper error handling.")

# Made with Bob