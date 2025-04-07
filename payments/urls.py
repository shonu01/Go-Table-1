from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('create-payment-intent/<int:booking_id>/', views.create_payment_intent, name='create_payment_intent'),
    path('success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path('cancel/<int:booking_id>/', views.payment_cancel, name='payment_cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
] 