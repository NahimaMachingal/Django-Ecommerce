from django.urls import path
from . import views

app_name = 'adminn'  # Namespace for admin URLs


urlpatterns = [
    #path('products/', views.product_list, name='product_list'),
    #path('addproducts',views.add_product, name='add_product'),
    path('adminhome/',views.adminhome, name='adminhome'),
    path('signout/',views.signout, name='signout'),
    path('users/', views.users, name='users'),
    path('addproduct/', views.addproduct, name='addproduct'),
    path('productlist/', views.productlist, name='productlist'),
    path('addvariation/', views.addvariation, name='addvariation'),
    path('variationlist/', views.variationlist, name='variationlist'),
    path('process_order/<int:order_id>/', views.process_order, name='process_order'),
    path('ship_order/<int:order_id>/', views.ship_order, name='ship_order'),
    path('deliver_order/<int:order_id>/', views.deliver_order, name='deliver_order'),
    path('deleteproduct/<int:product_id>/', views.deleteproduct, name = 'deleteproduct'),
    path('editproduct/<int:product_id>/', views.editproduct, name = 'editproduct'),
    path('categorylist/', views.categorylist, name='categorylist'),
    path('addcategory/', views.addcategory, name='addcategory'),
    path('editcategory/<int:category_id>/', views.editcategory, name='editcategory'),
    path('deletecategory/<int:category_id>/', views.deletecategory, name='deletecategory'),
    path('orderlist/', views.orderlist, name='orderlist'),
    path('cancelorder/<int:order_id>/', views.cancelorder, name='cancelorder'),
    path('blockuser/<int:user_id>/', views.blockuser, name='blockuser'),
    path('order_detaill/<int:order_id>/', views.order_detaill, name='order_detaill'),
    path('unblockuser/<int:user_id>/', views.unblockuser, name='unblockuser'),
    path('coupon/', views.coupon, name='coupon'),
    path('add_coupon/', views.add_coupon, name='add_coupon'),
    #path('offers/create/', views.offer_creation_view, name='offer_create'),
    path('sales_report/', views.sales_report, name='sales_report'),
    path('sales/daily/', views.sales_report, {'period': 'daily'}, name='daily_sales_report'),
    path('sales/weekly/', views.sales_report, {'period': 'weekly'}, name='weekly_sales_report'),
    path('sales/monthly/', views.sales_report, {'period': 'monthly'}, name='monthly_sales_report'),
    path('sales/yearly/', views.sales_report, {'period': 'yearly'}, name='yearly_sales_report'),
    path('sales/custom/', views.sales_report, {'period': 'custom'}, name='custom_sales_report'),
    path('coupon/<int:coupon_id>/delete/', views.delete_coupon, name='delete_coupon'),
    path('custom_admin_homepage/', views.custom_admin_homepage, name='custom_admin_homepage'),
    path('sales_report/pdf/', views.download_sales_reportpdf, name='download_sales_reportpdf'),
    path('sales_report/excel/', views.download_sales_reportexcel, name='download_sales_reportexcel'),
    
]
