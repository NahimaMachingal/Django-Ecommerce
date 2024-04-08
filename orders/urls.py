from django.urls import path
from . import views

urlpatterns = [
        path('place_order/', views.place_order, name='place_order'),
        path('payments/', views.payments, name='payments'),
        path('cash_on_delivery/<str:order_number>/', views.cash_on_delivery, name='cash_on_delivery'),
        path('add_to_wallet/<str:order_number>/', views.add_to_wallet, name='add_to_wallet'),
        #path('confirmpayment/<str:order_number>/', views.confirmpayment, name='confirmpayment'),
        #path('add_address/', views.add_address, name='add_address'),
        path('order_complete/', views.order_complete, name='order_complete'),
        path('cancel_order/<str:order_number>/', views.cancel_order, name='cancel_order'),
        path('cancell_order/<str:order_number>/', views.cancell_order, name='cancell_order'),


]