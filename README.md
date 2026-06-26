# E-Commerce Shopping Cart

A Python-based e-commerce platform with product listings, shopping cart functionality, and secure payment processing using Stripe.

## Features

- 🛍️ **Product Listings** - Browse and search products
- 🛒 **Shopping Cart** - Add/remove items, persistent cart storage
- 💳 **Secure Payment** - Stripe integration for safe transactions
- 👤 **User Authentication** - Register and login functionality
- 📦 **Order Management** - Track order history and status
- 🔒 **Security** - Encrypted passwords, CSRF protection, secure sessions

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Payment**: Stripe API
- **Frontend**: HTML5, CSS3, Bootstrap, JavaScript
- **Authentication**: Flask-Login with bcrypt
- **Testing**: pytest, unittest

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── models.py          # Database models
│   ├── routes.py          # Flask blueprints
│   ├── forms.py           # WTForms forms
│   ├── payment.py         # Payment processing
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── products.html
│       ├── product_detail.html
│       ├── cart.html
│       ├── checkout.html
│       ├── login.html
│       └── register.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── cart.js
├── tests/
│   ├── test_models.py
│   ├── test_routes.py
│   └── test_payment.py
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
└── run.py                 # Application entry point
```

## Installation

1. Clone the repository
```bash
git clone https://github.com/weriodplanet-ops/E-COMMERCE-SHOPPING-CART.git
cd E-COMMERCE-SHOPPING-CART
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your Stripe keys and configuration
```

5. Initialize the database
```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

6. Run the application
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## Environment Variables

```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///ecommerce.db
STRIPE_PUBLIC_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
```

## API Endpoints

### Products
- `GET /` - Homepage with featured products
- `GET /products` - All products
- `GET /products/<id>` - Product details

### Cart
- `POST /cart/add/<product_id>` - Add to cart
- `GET /cart` - View cart
- `POST /cart/remove/<product_id>` - Remove from cart
- `POST /cart/update` - Update quantities

### Checkout
- `GET /checkout` - Checkout page
- `POST /checkout/process` - Process payment

### Auth
- `POST /register` - Create account
- `POST /login` - Login
- `GET /logout` - Logout

## Payment Processing

The application uses Stripe for secure payment processing:

1. Customer fills cart and proceeds to checkout
2. Stripe form collects payment information securely
3. Backend validates cart and creates payment intent
4. Payment is processed through Stripe API
5. Order is created and stored in database
6. Confirmation email is sent

## Security Considerations

- ✅ Passwords hashed with bcrypt
- ✅ CSRF tokens on all forms
- ✅ SQL injection protected via SQLAlchemy ORM
- ✅ XSS protection with template escaping
- ✅ Secure session management
- ✅ HTTPS ready (configure in production)
- ✅ PCI compliance through Stripe

## Testing

Run tests with:
```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please create an issue on GitHub.

---

**Status**: Under Development
**Last Updated**: June 26, 2026