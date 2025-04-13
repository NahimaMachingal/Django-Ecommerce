# 🛍️ Django Ecommerce

A web-based shopping platform built with Django and Django Template Language.

---

## 📌 Overview

**Django Ecommerce** is a fully functional e-commerce system featuring product management, user authentication, cart operations, order tracking, and payment integration. It’s designed with scalability and customization in mind, making it an ideal base for any online store.

---

## ✨ Features

- 🔐 User Authentication (Signup, Login, Logout)
- 🛍️ Product Listing with Detailed Product Pages
- 🛒 Shopping Cart Functionality
- 📦 Order Placement and Tracking
- 💳 Secure Checkout with Payment Gateway Integration
- 🧾 PDF Invoice Generation
- 🛠️ Admin Panel for Product and Order Management
- 📱 SMS Notifications via Twilio

---

## 🛠️ Technologies Used

| Component        | Technology                         |
|------------------|-------------------------------------|
| **Backend**      | Django, Django Template Language    |
| **Database**     | PostgreSQL                          |
| **Authentication** | Django Allauth, JWT              |
| **Payment Gateway** | Integrated via External APIs    |
| **PDF Invoices** | WeasyPrint                          |
| **SMS**          | Twilio API                          |

---

# Installation Guide

## 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

## 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 4. Configure the Database
Update `settings.py` with your PostgreSQL credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## 6. Create a Superuser
```bash
python manage.py createsuperuser
```
Follow the prompts to set up an admin account.

## 7. Run the Server
```bash
python manage.py runserver
```
Visit: http://127.0.0.1:8000/

## 🚀 How to Use
- Register or log in as a user.
- Browse products and add items to the cart.
- Proceed to checkout and place an order.
- Admins can manage products and orders at `/admin/`.

## 🌐 Deployment
To deploy in a production environment, use Gunicorn with NGINX as a reverse proxy.

### Example Gunicorn Command
```bash
gunicorn --bind 0.0.0.0:8000 myproject.wsgi
```

## 📄 License
This project is licensed under the MIT License.

## 🤝 Contributing
Pull requests are welcome!
Feel free to fork the repository and submit your changes.

## 📬 Contact
For any queries or support, reach out via GitHub Issues.
