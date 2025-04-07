from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.booking_list, name='list'),
    path('create/<int:restaurant_id>/', views.booking_create, name='create'),
    path('<int:pk>/', views.booking_detail, name='detail'),
    path('<int:pk>/update/', views.booking_update, name='update'),
    path('<int:pk>/delete/', views.booking_delete, name='delete'),

    path('<int:booking_id>/payment/create/', views.payment_create, name='payment_create'),
    path('payment/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('payment/history/', views.payment_history, name='payment_history'),
]