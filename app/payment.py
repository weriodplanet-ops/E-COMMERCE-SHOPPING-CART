import stripe
import os
from app.models import Order, OrderItem, Product
from app import db

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class PaymentProcessor:
    """Handle Stripe payment processing"""
    
    @staticmethod
    def create_payment_intent(cart, amount):
        """
        Create a Stripe PaymentIntent
        
        Args:
            cart: Cart object
            amount: Total amount in cents
        
        Returns:
            PaymentIntent object or None if error
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'user_id': cart.user_id,
                    'cart_id': cart.id
                }
            )
            return intent
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            return None
    
    @staticmethod
    def confirm_payment(payment_intent_id):
        """
        Confirm a payment intent
        
        Args:
            payment_intent_id: ID of the payment intent
        
        Returns:
            PaymentIntent object or None if error
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return intent
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            return None
    
    @staticmethod
    def create_order_from_cart(user, cart, payment_intent_id, shipping_address, billing_address, notes):
        """
        Create an Order from Cart after successful payment
        
        Args:
            user: User object
            cart: Cart object
            payment_intent_id: Stripe payment intent ID
            shipping_address: Shipping address string
            billing_address: Billing address string
            notes: Order notes
        
        Returns:
            Order object or None if error
        """
        try:
            total_amount = cart.get_total()
            
            order = Order(
                user_id=user.id,
                total_amount=total_amount,
                status='processing',
                payment_method='stripe',
                stripe_payment_intent_id=payment_intent_id,
                shipping_address=shipping_address,
                billing_address=billing_address or shipping_address,
                notes=notes
            )
            
            # Copy cart items to order
            for cart_item in cart.items:
                order_item = OrderItem(
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                order.items.append(order_item)
                
                # Update product stock
                product = Product.query.get(cart_item.product_id)
                if product:
                    product.stock -= cart_item.quantity
            
            db.session.add(order)
            db.session.commit()
            
            # Clear the cart
            from app.models import CartItem
            CartItem.query.filter_by(cart_id=cart.id).delete()
            db.session.commit()
            
            return order
        except Exception as e:
            print(f"Error creating order: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_customer_payment_methods(customer_id):
        """
        Get payment methods for a customer
        
        Args:
            customer_id: Stripe customer ID
        
        Returns:
            List of payment method objects
        """
        try:
            methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )
            return methods.data
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            return []
    
    @staticmethod
    def refund_order(order):
        """
        Refund an order
        
        Args:
            order: Order object
        
        Returns:
            Refund object or None if error
        """
        try:
            refund = stripe.Refund.create(
                payment_intent=order.stripe_payment_intent_id
            )
            order.status = 'refunded'
            db.session.commit()
            return refund
        except stripe.error.StripeError as e:
            print(f"Stripe error: {e}")
            return None