from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from .forms import AdminRegistrationForm, AdminLoginForm
from restaurants.models import Restaurant
from bookings.models import Booking
from accounts.models import CustomUser
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone

def admin_register(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Admin account created successfully!')
            return redirect('admin_panel:dashboard')
    else:
        form = AdminRegistrationForm()
    return render(request, 'admin_panel/register.html', {'form': form})

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and hasattr(user, 'admin_profile'):
                login(request, user)
                messages.success(request, 'Welcome back!')
                return redirect('admin_panel:dashboard')
            else:
                messages.error(request, 'Invalid credentials or not an admin account.')
    else:
        form = AdminLoginForm()
    return render(request, 'admin_panel/login.html', {'form': form})

class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'admin_panel/dashboard.html'
    login_url = 'admin_panel:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_restaurants'] = Restaurant.objects.count()
        context['total_bookings'] = Booking.objects.count()
        context['total_users'] = CustomUser.objects.count()
        context['recent_bookings'] = Booking.objects.order_by('-created_at')[:5]
        context['recent_restaurants'] = Restaurant.objects.order_by('-created_at')[:5]
        return context

class RestaurantListView(LoginRequiredMixin, ListView):
    model = Restaurant
    template_name = 'admin_panel/restaurant_list.html'
    context_object_name = 'restaurants'
    paginate_by = 10

class RestaurantDetailView(LoginRequiredMixin, DetailView):
    model = Restaurant
    template_name = 'admin_panel/restaurant_detail.html'
    context_object_name = 'restaurant'

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'admin_panel/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10

class UserListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'admin_panel/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

@staff_member_required
def restaurant_management(request):
    restaurants = Restaurant.objects.all().order_by('-created_at')
    context = {
        'restaurants': restaurants,
        'title': 'Restaurant Management',
    }
    return render(request, 'admin/restaurant_management.html', context)

@staff_member_required
def booking_management(request):
    pending_bookings = Booking.objects.filter(status='pending').order_by('-created_at')
    approved_bookings = Booking.objects.filter(status='approved').order_by('-created_at')
    rejected_bookings = Booking.objects.filter(status='rejected').order_by('-created_at')
    
    context = {
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'rejected_bookings': rejected_bookings,
        'title': 'Booking Management',
    }
    return render(request, 'admin/booking_management.html', context)

@staff_member_required
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'approved'
    booking.save()
    messages.success(request, f'Booking #{booking.id} has been approved')
    return redirect('admin:booking-management')

@staff_member_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'rejected'
    booking.save()
    messages.success(request, f'Booking #{booking.id} has been rejected')
    return redirect('admin:booking-management')

@staff_member_required
def rate_restaurant(request, restaurant_id):
    if request.method == 'POST':
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        rating = request.POST.get('rating')
        if rating and rating.isdigit():
            restaurant.rating = int(rating)
            restaurant.save()
            messages.success(request, f'Rating updated for {restaurant.name}')
    return redirect('admin:restaurant-management')
