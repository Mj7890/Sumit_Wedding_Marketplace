from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('card/<slug:slug>/', views.card_detail, name='card_detail'),
    path('card/<slug:slug>/customize/', views.customize_card, name='customize_card'),
    path('cart/', views.cart, name='cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('register/', views.register_step1, name='register'),
    path('register/step1/', views.register_step1, name='register_step1'),
    path('register/step2/', views.register_step2, name='register_step2'),
    path('register/step2/resend/', views.resend_otp, name='resend_otp'),
    path('register/step3/', views.register_step3, name='register_step3'),
    path('printer-card/', views.printer_card_form, name='printer_card_form'),
    path('printer-card/success/<int:pk>/', views.printer_card_success, name='printer_card_success'),
    path('printer-card/my-orders/', views.my_printer_orders, name='my_printer_orders'),
    # Dashboard & Admin Upload
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-upload/', views.admin_upload_collection, name='admin_upload_collection'),
    path('search-suggestions/', views.search_api, name='search_suggestions'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
