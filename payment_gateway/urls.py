from django.urls import path
from . import views

app_name = 'payment_gateway'

urlpatterns = [
    path('create/<int:booking_id>/', views.payment_create, name='payment_create'),
    path('detail/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('history/', views.payment_history, name='payment_history'),
    path('refund/<int:payment_id>/', views.refund_request, name='refund_request'),
    path('webhook/', views.razorpay_webhook, name='razorpay_webhook'),
] 