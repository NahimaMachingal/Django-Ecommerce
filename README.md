Django Ecommerce

Overview

Django Ecommerce is a web-based shopping platform built using Django Template Language. This project provides a fully functional e-commerce system with features like product management, user authentication, shopping cart, order processing, and payment integration.

Features

User authentication (signup, login, logout)

Product listing and detailed product pages

Shopping cart functionality

Order placement and tracking

Secure checkout with payment gateway integration

PDF invoice generation

Admin panel for product and order management

Technologies Used

Backend: Django, Django Template Language

Database: PostgreSQL

Authentication: Django Allauth, JWT

Payment Gateway: Integrated with external APIs

Additional Features: PDF invoice generation using WeasyPrint, Twilio for SMS notifications

Installation

1. Clone the Repository

 git clone https://github.com/NahimaMachingal/Django-Ecommerce.git
 cd Django-Ecommerce

2. Create a Virtual Environment

 python -m venv venv
 source venv/bin/activate  # On Windows use: venv\Scripts\activate

3. Install Dependencies

 pip install -r requirements.txt

4. Configure the Database

Update the settings.py file with your PostgreSQL credentials.

Run migrations:

 python manage.py makemigrations
 python manage.py migrate

5. Create a Superuser

 python manage.py createsuperuser

Follow the prompts to set up an admin account.

6. Run the Server

 python manage.py runserver

Access the application at http://127.0.0.1:8000/

How to Use

Register/Login as a user

Browse products and add them to the cart

Proceed to checkout and place an order

Admins can manage products and orders from /admin/

Deployment

To deploy the project, you can use Gunicorn for a production WSGI server along with NGINX as a reverse proxy.

Example for Gunicorn:

 gunicorn --bind 0.0.0.0:8000 myproject.wsgi

License

This project is licensed under the MIT License.

Contributing

Pull requests are welcome! Feel free to fork the repository and submit changes.

Contact

For any queries, reach out via GitHub.

