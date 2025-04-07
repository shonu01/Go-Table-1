from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import Booking
from .forms import BookingForm
from restaurants.models import Restaurant
from django.utils import timezone
from payments.models import Payment
from django.core.paginator import Paginator
from django.db.models import Q


@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date', '-booking_time')
    return render(request, 'bookings/booking_list.html', {'bookings': bookings})

@login_required
def booking_create(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # Update user's contact info
            request.user.phone_number = form.cleaned_data['phone_number']
            request.user.save()
            
            # Create the booking
            booking = form.save(commit=False)
            booking.user = request.user
            booking.restaurant = restaurant
            booking.save()
            
            messages.success(request, 'Booking created successfully! We will notify you when the restaurant confirms your booking.')
            return redirect('bookings:list')
    else:
        initial_data = {}
        if request.user.phone_number:
            initial_data['phone_number'] = request.user.phone_number
        form = BookingForm(initial=initial_data)
    
    return render(request, 'bookings/booking_form.html', {
        'form': form,
        'restaurant': restaurant
    })


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

@login_required
def booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated successfully!')
            return redirect('bookings:detail', pk=booking.pk)
    else:
        form = BookingForm(instance=booking)
    return render(request, 'bookings/booking_form.html', {'form': form, 'booking': booking, 'restaurant': booking.restaurant})

@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted successfully!')
        return redirect('bookings:list')
    return render(request, 'bookings/booking_confirm_delete.html', {'booking': booking})

@login_required
def payment_create(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        payment = Payment.objects.create(
            booking=booking,
            amount=amount,
            payment_method=payment_method
        )
        messages.success(request, 'Payment processed successfully!')
        return redirect('bookings:detail', pk=booking.pk)
    return render(request, 'bookings/payment_form.html', {'booking': booking})

@login_required
def payment_detail(request, pk):
    payment = get_object_or_404(Payment, pk=pk, booking__user=request.user)
    return render(request, 'bookings/payment_detail.html', {'payment': payment})

@login_required
def payment_history(request):
    payments = Payment.objects.filter(booking__user=request.user).order_by('-created_at')
    paginator = Paginator(payments, 10)
    page = request.GET.get('page')
    payments = paginator.get_page(page)
    return render(request, 'bookings/payment_history.html', {'payments': payments})
