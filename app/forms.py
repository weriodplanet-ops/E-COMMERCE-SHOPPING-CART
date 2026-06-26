from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from app.models import User

class RegistrationForm(FlaskForm):
    """User registration form"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=80, message='Username must be between 3 and 80 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, field):
        """Check if username already exists"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken.')
    
    def validate_email(self, field):
        """Check if email already exists"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AddToCartForm(FlaskForm):
    """Add to cart form"""
    quantity = IntegerField('Quantity', validators=[
        DataRequired(),
        NumberRange(min=1, max=1000, message='Quantity must be between 1 and 1000')
    ])
    submit = SubmitField('Add to Cart')

class UpdateCartForm(FlaskForm):
    """Update cart quantities form"""
    quantities = StringField('Quantities')
    submit = SubmitField('Update Cart')

class CheckoutForm(FlaskForm):
    """Checkout form"""
    shipping_address = TextAreaField('Shipping Address', validators=[
        DataRequired(),
        Length(min=10, message='Please enter a valid address')
    ])
    billing_address = TextAreaField('Billing Address')
    notes = TextAreaField('Order Notes')
    submit = SubmitField('Proceed to Payment')

class PaymentForm(FlaskForm):
    """Payment form"""
    submit = SubmitField('Complete Payment')