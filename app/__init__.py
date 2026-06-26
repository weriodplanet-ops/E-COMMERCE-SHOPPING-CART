from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Create app context
    with app.app_context():
        # Import models
        from app.models import User, Product, Cart, Order, OrderItem
        
        # Create database tables
        db.create_all()
        
        # Register blueprints
        from app.routes import auth_bp, products_bp, cart_bp, orders_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(products_bp)
        app.register_blueprint(cart_bp)
        app.register_blueprint(orders_bp)
        
        # User loader
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))
    
    return app