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
from django.db import IntegrityError
import razorpay
import json
from django.http import JsonResponse, HttpResponse
from decimal import Decimal
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from datetime import datetime

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

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
            try:
                # Check if there's already a booking for this time slot
                existing_booking = Booking.objects.filter(
                    restaurant=restaurant,
                    booking_date=form.cleaned_data['booking_date'],
                    booking_time=form.cleaned_data['booking_time']
                ).first()
                
                if existing_booking:
                    messages.error(
                        request,
                        f'Sorry, this time slot is already booked. Please choose a different time.'
                    )
                else:
                    # Update user's contact info
                    request.user.phone_number = form.cleaned_data['phone_number']
                    request.user.save()
                    
                    # Calculate amount based on party size (₹100 per person)
                    party_size = form.cleaned_data['party_size']
                    amount = Decimal(party_size * 100)
                    
                    # Create the booking with pending payment status
                    booking = form.save(commit=False)
                    booking.user = request.user
                    booking.restaurant = restaurant
                    booking.amount = amount
                    booking.payment_status = 'pending'
                    booking.save()
                    
                    # Create Razorpay order (amount in paise)
                    amount_in_paise = int(amount * 100)  # Convert to paise
                    currency = 'INR'
                    payment = razorpay_client.order.create({
                        'amount': amount_in_paise,
                        'currency': currency,
                        'payment_capture': '1'
                    })
                    
                    # Store payment details in session
                    request.session['razorpay_order_id'] = payment['id']
                    request.session['booking_id'] = booking.id
                    
                    context = {
                        'booking': booking,
                        'razorpay_order_id': payment['id'],
                        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                        'amount': amount_in_paise,  # Amount in paise for Razorpay
                        'currency': currency,
                        'user_name': request.user.get_full_name(),
                        'user_email': request.user.email,
                        'user_phone': request.user.phone_number
                    }
                    
                    return render(request, 'bookings/payment.html', context)
                    
            except IntegrityError:
                messages.error(
                    request,
                    'Sorry, this time slot was just booked by someone else. Please choose a different time.'
                )
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

@login_required
def payment_callback(request):
    if request.method == 'POST':
        try:
            # Get the payment details from the request
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            
            # Verify the payment signature
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            }
            
            razorpay_client.utility.verify_payment_signature(params_dict)
            
            # Get the booking from session
            booking_id = request.session.get('booking_id')
            if not booking_id:
                messages.error(request, 'Booking session expired. Please try again.')
                return redirect('bookings:list')
                
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)
            
            # Update booking status
            booking.payment_status = 'completed'
            booking.status = 'confirmed'
            booking.save()
            
            # Create payment record
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.amount,  # Use the booking amount in rupees
                payment_method='razorpay',
                transaction_id=payment_id,
                status='completed'
            )
            
            # Clear session data
            request.session.pop('razorpay_order_id', None)
            request.session.pop('booking_id', None)
            
            messages.success(request, 'Payment successful! Your booking is confirmed.')
            return redirect('bookings:detail', pk=booking.id)
            
        except Exception as e:
            messages.error(request, f'Payment verification failed: {str(e)}')
            # Update booking status to failed
            if booking_id := request.session.get('booking_id'):
                try:
                    booking = Booking.objects.get(id=booking_id)
                    booking.payment_status = 'failed'
                    booking.save()
                except Booking.DoesNotExist:
                    pass
            return redirect('bookings:list')
    
    return redirect('bookings:list')

@login_required
def download_invoice(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    
    # Create a BytesIO buffer to receive the PDF data
    buffer = BytesIO()
    
    # Create the PDF object, using the buffer as its "file"
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12
    )
    normal_style = styles['Normal']
    
    # Add company logo and title
    elements.append(Paragraph("GoTable", title_style))
    elements.append(Paragraph("Booking Invoice", heading_style))
    elements.append(Spacer(1, 20))
    
    # Add booking details
    elements.append(Paragraph("Booking Details", heading_style))
    booking_data = [
        ["Booking ID:", f"#{booking.id}"],
        ["Date:", booking.booking_date.strftime("%B %d, %Y")],
        ["Time:", booking.booking_time.strftime("%I:%M %p")],
        ["Status:", booking.status.title()],
        ["Party Size:", str(booking.party_size)],
    ]
    if booking.special_requests:
        booking_data.append(["Special Requests:", booking.special_requests])
    
    # Create booking details table
    booking_table = Table(booking_data, colWidths=[150, 350])
    booking_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(booking_table)
    elements.append(Spacer(1, 20))
    
    # Add restaurant details
    elements.append(Paragraph("Restaurant Details", heading_style))
    restaurant_data = [
        ["Name:", booking.restaurant.name],
        ["Address:", f"{booking.restaurant.address}, {booking.restaurant.city}"],
        ["Phone:", booking.restaurant.phone],
        ["Email:", booking.restaurant.email],
    ]
    
    # Create restaurant details table
    restaurant_table = Table(restaurant_data, colWidths=[150, 350])
    restaurant_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(restaurant_table)
    elements.append(Spacer(1, 20))
    
    # Add payment details
    elements.append(Paragraph("Payment Details", heading_style))
    payment = Payment.objects.filter(booking=booking, status='completed').first()
    if payment:
        payment_data = [
            ["Amount per Person:", "₹100.00"],
            ["Total Amount:", f"₹{booking.amount}"],
            ["Payment Method:", payment.payment_method.title()],
            ["Transaction ID:", payment.transaction_id],
            ["Payment Date:", payment.created_at.strftime("%B %d, %Y %I:%M %p")],
        ]
        
        # Create payment details table
        payment_table = Table(payment_data, colWidths=[150, 350])
        payment_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(payment_table)
    
    # Add footer
    elements.append(Spacer(1, 50))
    elements.append(Paragraph("Thank you for choosing GoTable!", normal_style))
    elements.append(Paragraph("For any queries, please contact our support team.", normal_style))
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="booking_invoice_{booking.id}.pdf"'
    response.write(pdf)
    
    return response
