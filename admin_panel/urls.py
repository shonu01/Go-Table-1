from django.urls import path, include
from . import views
from .admin_site import admin_site

app_name = 'admin_panel'

urlpatterns = [
    path('login/', views.admin_login, name='login'),
    path('register/', views.admin_register, name='register'),
    path('dashboard/', views.AdminDashboardView.as_view(), name='dashboard'),
    path('restaurants/', views.RestaurantListView.as_view(), name='restaurant_list'),
    path('restaurants/<int:pk>/', views.RestaurantDetailView.as_view(), name='restaurant_detail'),
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('restaurant-management/', views.restaurant_management, name='restaurant-management'),
    path('booking-management/', views.booking_management, name='booking-management'),
    path('booking/<int:booking_id>/approve/', views.approve_booking, name='approve-booking'),
    path('booking/<int:booking_id>/reject/', views.reject_booking, name='reject-booking'),
    path('restaurant/<int:restaurant_id>/rate/', views.rate_restaurant, name='rate-restaurant'),
]