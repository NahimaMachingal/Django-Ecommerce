from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_home, name='user_home'),
    path('login/', views.user_login, name='login'),
    path('register/',views.user_register, name='user_register'),
]