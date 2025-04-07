from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.db.models import Count, Avg
from restaurants.models import Restaurant
from bookings.models import Booking
from django.contrib.auth import get_user_model, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from restaurants.admin import RestaurantAdmin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from accounts.models import CustomUser

User = get_user_model()

def is_staff_user(user):
    return user.is_staff

class GoTableAdminSite(admin.AdminSite):
    site_header = 'GoTable Administration'
    site_title = 'GoTable Admin'
    index_title = 'Admin Dashboard'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.index), name='index'),
            path('restaurant-management/', self.admin_view(self.restaurant_management), name='restaurant_management'),
            path('user-management/', self.admin_view(self.user_management), name='user_management'),
            path('booking-management/', self.admin_view(self.booking_management), name='booking_management'),
            path('api/toggle-restaurant-status/<int:restaurant_id>/', self.admin_view(self.toggle_restaurant_status), name='toggle_restaurant_status'),
            path('api/get-dashboard-stats/', self.admin_view(self.get_dashboard_stats), name='get_dashboard_stats'),
            path('booking/approve/<int:booking_id>/', self.admin_view(self.approve_booking), name='approve_booking'),
            path('booking/reject/<int:booking_id>/', self.admin_view(self.reject_booking), name='reject_booking'),
            path('logout/', self.logout_view, name='logout'),
        ]
        return custom_urls + urls

    def index(self, request):
        # Get statistics for dashboard
        total_restaurants = Restaurant.objects.count()
        total_bookings = Booking.objects.count()
        total_users = User.objects.count()
        
        # Get recent bookings
        recent_bookings = Booking.objects.select_related('restaurant', 'user').order_by('-created_at')[:5]
        
        # Get top rated restaurants
        top_restaurants = Restaurant.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            booking_count=Count('bookings')
        ).order_by('-avg_rating')[:5]
        
        # Get recent activity
        recent_activity = []
        
        # Add recent bookings to activity
        for booking in Booking.objects.select_related('user', 'restaurant').order_by('-created_at')[:10]:
            recent_activity.append({
                'type': 'booking',
                'message': f'{booking.user.get_full_name()} booked {booking.restaurant.name}',
                'timestamp': booking.created_at
            })
        
        # Add recent restaurants to activity
        for restaurant in Restaurant.objects.order_by('-created_at')[:5]:
            recent_activity.append({
                'type': 'restaurant',
                'message': f'New restaurant added: {restaurant.name}',
                'timestamp': restaurant.created_at
            })
        
        # Sort activity by timestamp
        recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
        recent_activity = recent_activity[:10]
        
        context = {
            'total_restaurants': total_restaurants,
            'total_bookings': total_bookings,
            'total_users': total_users,
            'recent_bookings': recent_bookings,
            'top_restaurants': top_restaurants,
            'recent_activity': recent_activity,
            'title': 'Dashboard',
            **self.each_context(request),
        }
        
        return render(request, 'admin/index.html', context)

    def restaurant_management(self, request):
        restaurants = Restaurant.objects.annotate(
            booking_count=Count('bookings'),
            avg_rating=Avg('reviews__rating')
        ).order_by('-created_at')
        
        context = {
            'restaurants': restaurants,
            'title': 'Restaurant Management',
            **self.each_context(request),
        }
        return render(request, 'admin/restaurant_management.html', context)

    def user_management(self, request):
        users = User.objects.annotate(
            booking_count=Count('bookings'),
            restaurant_count=Count('restaurants')
        ).select_related('admin_profile').order_by('-date_joined')
        
        context = {
            'users': users,
            'title': 'User Management',
            **self.each_context(request),
        }
        return render(request, 'admin/user_management.html', context)

    def booking_management(self, request):
        bookings = Booking.objects.select_related('restaurant', 'user').order_by('-created_at')
        
        context = {
            'bookings': bookings,
            'title': 'Booking Management',
            **self.each_context(request),
        }
        return render(request, 'admin/booking_management.html', context)

    def logout_view(self, request):
        logout(request)
        return redirect('admin:login')

    @csrf_exempt
    def toggle_restaurant_status(self, request, restaurant_id):
        if request.method == 'POST':
            try:
                restaurant = Restaurant.objects.get(id=restaurant_id)
                restaurant.is_active = not restaurant.is_active
                restaurant.save()
                return JsonResponse({
                    'status': 'success',
                    'is_active': restaurant.is_active
                })
            except Restaurant.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Restaurant not found'
                }, status=404)
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        }, status=400)

    def get_dashboard_stats(self, request):
        # Get date range
        days = int(request.GET.get('days', 7))
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get daily bookings
        daily_bookings = Booking.objects.filter(
            created_at__range=(start_date, end_date)
        ).extra(
            select={'day': 'DATE(created_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        # Get daily revenue
        daily_revenue = Booking.objects.filter(
            created_at__range=(start_date, end_date)
        ).extra(
            select={'day': 'DATE(created_at)'}
        ).values('day').annotate(
            revenue=Count('id')  # This should be changed to sum actual revenue when implemented
        ).order_by('day')
        
        return JsonResponse({
            'daily_bookings': list(daily_bookings),
            'daily_revenue': list(daily_revenue)
        })

    def send_booking_status_email(self, booking, status):
        subject = f'Booking {status.title()} - {booking.restaurant.name}'
        
        # Different email templates based on status
        if status == 'approved':
            message = f"""
            Dear {booking.user.get_full_name()},
            
            Your booking at {booking.restaurant.name} has been approved!
            
            Booking Details:
            Date: {booking.booking_date}
            Time: {booking.booking_time}
            Party Size: {booking.party_size}
            
            Your OTP: {booking.otp}
            Please show this OTP when you arrive at the restaurant.
            
            Thank you for choosing {booking.restaurant.name}!
            """
        else:  # rejected
            message = f"""
            Dear {booking.user.get_full_name()},
            
            We regret to inform you that your booking at {booking.restaurant.name} could not be accommodated.
            
            Booking Details:
            Date: {booking.booking_date}
            Time: {booking.booking_time}
            Party Size: {booking.party_size}
            
            Please try booking for a different time or date.
            
            Thank you for your understanding.
            """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.user.email],
            fail_silently=False,
        )

    def update_booking_status(self, request, booking_id, status):
        booking = Booking.objects.get(id=booking_id)
        booking.status = status
        booking.save()
        
        # Send email notification
        self.send_booking_status_email(booking, status)
        
        messages.success(request, f'Booking {status} successfully')
        return redirect('admin:booking_management')

    def approve_booking(self, request, booking_id):
        return self.update_booking_status(request, booking_id, 'approved')

    def reject_booking(self, request, booking_id):
        return self.update_booking_status(request, booking_id, 'rejected')

admin_site = GoTableAdminSite(name='admin')
admin_site.register(Restaurant, RestaurantAdmin)