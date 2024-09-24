from django.urls import path
from . import views

urlpatterns = [
    # Google authentication
    path("login/google",views.login_with_google,name="google_login"),
    path("google/login/callback/",views.google_callback,name="google_callback"),
    path('register/', views.register, name='register'),
    path('loginn/', views.loginn, name='loginn'),
    path('logout/', views.logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    #path('otp/<str:uid>/', views.otpVerify, name='otp'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),
    path('forgotpassword/', views.forgotpassword, name='forgotpassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetpassword/', views.resetpassword, name='resetpassword'),
    path('generate_invoice_pdf/<int:order_number>/', views.generate_invoice_pdf, name='generate_invoice_pdf'),
    path('user_wallet/', views.user_wallet, name='user_wallet'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('invoice/<int:order_id>/', views.invoice, name='invoice'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('add_address/', views.add_address, name='add_address'),
    path('return_order/<str:order_number>/', views.return_order, name='return_order'),
    path('cancel_orderr/<str:order_number>/', views.cancel_orderr, name='cancel_orderr'),



]   