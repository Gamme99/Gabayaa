# Django Ecommerce Project

This is a Django-based Ecommerce Project that allows sellers to list products and buyers to purchase them. 
The project is equipped with integrated payment gateways Stripe and PayPal to facilitate seamless transactions.

## Features

- **Seller Dashboard**
  - Sellers can register and log in to their accounts.
  - Add, edit, and delete products they want to sell.
  - View order history and manage orders.

- **Buyer Dashboard**
  - Buyers can register and log in to their accounts.
  - Browse products by category and search for specific items.
  - Add products to their cart and proceed to checkout.
  - Pay for products using Stripe or PayPal.
  - View order history and order details.

- **Payment Integration**
  - Stripe and PayPal are integrated for secure and convenient payments.
  - Users can make payments using their preferred payment method.

- **Product Management**
  - Sellers can add detailed product information, including images, descriptions, and prices.
  - Product listings are categorized for easy navigation.

## Installation

1. **Clone the Repository**
   ```
   git clone https://github.com/gamme99/gabaya.git
   ```

2. **Create a Virtual Environment**
   ```
   python -m venv gby
   ```

3. **Activate the Virtual Environment**
   - On Windows:
     ```
     gby\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source gby/bin/activate
     ```

4. **Install Dependencies**
   ```
   pip install -r requirements.txt
   ```

5. **Apply Migrations**
   ```
   python manage.py migrate
   ```

6. **Create Superuser (Admin)**
   ```
   python manage.py createsuperuser
   ```

7. **Run the Development Server**
   ```
   python manage.py runserver
   ```

8. **Access the Application**
   - Open a web browser and navigate to `http://localhost:8000/` to access the application.

## Configuration

Before initiating the project, take a moment to configure these settings to enjoy the application to its fullest extent:

### Stripe Integration

1. Sign up for a Stripe account at [https://stripe.com/](https://stripe.com/).
2. Obtain your Stripe API keys (publishable key and secret key).
3. Update `settings.py` which gets Stripe API keys from .env file:

   ```python
   STRIPE_PUBLISHABLE_KEY = 'your-publishable-key'
   STRIPE_SECRET_KEY = 'your-secret-key'
   ```

### PayPal Integration

1. Sign up for a PayPal account at [https://www.paypal.com/](https://www.paypal.com/).
2. Create a PayPal REST API application and obtain the client ID and secret.
3. Update `settings.py` which gets PayPal credentials from .env file:

   ```python
   PAYPAL_CLIENT_ID = 'your-client-id'
   PAYPAL_SECRET_KEY = 'your-secret-key'
   ```

Happy selling and shopping!
