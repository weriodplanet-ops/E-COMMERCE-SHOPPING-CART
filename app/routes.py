from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Product, Cart, CartItem, Order
from app.forms import RegistrationForm, LoginForm, AddToCartForm, CheckoutForm
from app.payment import PaymentProcessor
import os

# Create blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
products_bp = Blueprint('products', __name__, url_prefix='/products')
cart_bp = Blueprint('cart', __name__, url_prefix='/cart')
orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

# ==================== AUTH ROUTES ====================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('products.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # Create empty cart for user
        cart = Cart(user_id=user.id)
        db.session.add(cart)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('products.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('products.home'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('products.home'))

# ==================== PRODUCT ROUTES ====================

@products_bp.route('/')
@products_bp.route('/home')
def home():
    """Homepage with featured products"""
    page = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(is_active=True).paginate(page=page, per_page=12)
    return render_template('index.html', products=products)

@products_bp.route('/all')
def list_products():
    """All products page"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Product.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Product.name.ilike(f'%{search}%') | Product.description.ilike(f'%{search}%'))
    
    products = query.paginate(page=page, per_page=12)
    return render_template('products.html', products=products, search=search, category=category)

@products_bp.route('/<int:product_id>')
def product_detail(product_id):
    """Product detail page"""
    product = Product.query.get_or_404(product_id)
    form = AddToCartForm()
    return render_template('product_detail.html', product=product, form=form)

# ==================== CART ROUTES ====================

@cart_bp.route('/')
@login_required
def view_cart():
    """View shopping cart"""
    cart = current_user.cart
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
    
    return render_template('cart.html', cart=cart)

@cart_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """Add product to cart"""
    product = Product.query.get_or_404(product_id)
    
    form = AddToCartForm()
    if form.validate_on_submit():
        quantity = form.quantity.data
        
        # Get or create cart
        cart = current_user.cart
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
        
        # Check if product already in cart
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        
        if cart_item:
            cart_item.quantity += quantity
            flash(f'Updated {product.name} quantity in cart.', 'info')
        else:
            cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
            flash(f'Added {product.name} to cart.', 'success')
        
        db.session.commit()
    
    return redirect(request.referrer or url_for('cart.view_cart'))

@cart_bp.route('/remove/<int:cart_item_id>', methods=['POST'])
@login_required
def remove_from_cart(cart_item_id):
    """Remove item from cart"""
    cart_item = CartItem.query.get_or_404(cart_item_id)
    
    # Verify cart belongs to current user
    if cart_item.cart.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    product_name = cart_item.product.name
    db.session.delete(cart_item)
    db.session.commit()
    
    flash(f'Removed {product_name} from cart.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/update', methods=['POST'])
@login_required
def update_cart():
    """Update cart quantities"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    for item_id, quantity in data.items():
        cart_item = CartItem.query.get(int(item_id))
        if cart_item and cart_item.cart.user_id == current_user.id:
            if quantity <= 0:
                db.session.delete(cart_item)
            else:
                cart_item.quantity = quantity
    
    db.session.commit()
    return jsonify({'success': True})

# ==================== ORDER ROUTES ====================

@orders_bp.route('/')
@login_required
def list_orders():
    """List user's orders"""
    page = request.args.get('page', 1, type=int)
    orders = current_user.orders.paginate(page=page, per_page=10)
    return render_template('orders.html', orders=orders)

@orders_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    """View order details"""
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('orders.list_orders'))
    
    return render_template('order_detail.html', order=order)

@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Checkout page"""
    cart = current_user.cart
    if not cart or not cart.items.count():
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('products.home'))
    
    form = CheckoutForm()
    if form.validate_on_submit():
        total = cart.get_total()
        
        # Create payment intent
        intent = PaymentProcessor.create_payment_intent(cart, total)
        if intent:
            session['payment_intent_id'] = intent.id
            session['shipping_address'] = form.shipping_address.data
            session['billing_address'] = form.billing_address.data
            session['notes'] = form.notes.data
            return redirect(url_for('orders.payment'))
        else:
            flash('Payment processing error. Please try again.', 'danger')
    
    return render_template('checkout.html', form=form, cart=cart)

@orders_bp.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    """Payment processing page"""
    if 'payment_intent_id' not in session:
        flash('Invalid payment session.', 'danger')
        return redirect(url_for('cart.view_cart'))
    
    cart = current_user.cart
    intent = PaymentProcessor.confirm_payment(session['payment_intent_id'])
    
    if not intent:
        flash('Payment failed. Please try again.', 'danger')
        return redirect(url_for('orders.checkout'))
    
    if intent.status == 'succeeded':
        # Create order
        order = PaymentProcessor.create_order_from_cart(
            current_user,
            cart,
            intent.id,
            session.get('shipping_address'),
            session.get('billing_address'),
            session.get('notes')
        )
        
        if order:
            # Clear session
            session.pop('payment_intent_id', None)
            session.pop('shipping_address', None)
            session.pop('billing_address', None)
            session.pop('notes', None)
            
            flash('Payment successful! Your order has been placed.', 'success')
            return redirect(url_for('orders.order_detail', order_id=order.id))
        else:
            flash('Order creation failed. Please contact support.', 'danger')
    
    return render_template('payment.html', intent=intent, stripe_public_key=os.environ.get('STRIPE_PUBLIC_KEY'))