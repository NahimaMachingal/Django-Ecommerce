from django.urls import path
from . import views

urlpatterns = [
        path('place_order/', views.place_order, name='place_order'),
        path('payments/', views.payments, name='payments'),
        path('confirmpayment/<str:order_number>/', views.confirmpayment, name='confirmpayment'),
        #path('add_address/', views.add_address, name='add_address'),

]