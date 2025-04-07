from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bookings.models import Booking
from .models import Payment, PaymentRefund
from .forms import PaymentForm, PaymentRefundForm
import razorpay
import json
import hmac
import hashlib

# Initialize Razorpay
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def payment_create(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.user = request.user
            payment.save()
            
            if payment.payment_method == 'card':
                # Create Razorpay order
                order_data = {
                    'amount': int(payment.amount * 100),  # Convert to paise
                    'currency': 'INR',
                    'receipt': f'booking_{booking.id}',
                    'payment_capture': 1
                }
                
                try:
                    order = client.order.create(data=order_data)
                    payment.razorpay_order_id = order['id']
                    payment.save()
                    
                    return render(request, 'payment_gateway/razorpay_payment.html', {
                        'payment': payment,
                        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                        'order_id': order['id'],
                        'amount': payment.amount * 100,
                        'currency': 'INR',
                        'name': request.user.get_full_name(),
                        'email': request.user.email,
                        'contact': booking.phone_number
                    })
                except Exception as e:
                    messages.error(request, 'Failed to create payment order. Please try again.')
                    return redirect('bookings:detail', booking_id=booking.id)
            else:
                payment.status = 'completed'
                payment.save()
                messages.success(request, 'Payment completed successfully!')
                return redirect('bookings:detail', booking_id=booking.id)
    else:
        form = PaymentForm(initial={'amount': booking.total_amount})
    
    return render(request, 'payment_gateway/payment_form.html', {
        'form': form,
        'booking': booking
    })

@login_required
def payment_detail(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    return render(request, 'payment_gateway/payment_detail.html', {'payment': payment})

@login_required
def payment_history(request):
    payments = Payment.objects.filter(user=request.user).order_by('-payment_date')
    return render(request, 'payment_gateway/payment_history.html', {'payments': payments})

@login_required
def refund_request(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if request.method == 'POST':
        form = PaymentRefundForm(request.POST)
        if form.is_valid():
            refund = form.save(commit=False)
            refund.payment = payment
            refund.save()
            
            try:
                # Create Razorpay refund
                refund_data = {
                    'payment_id': payment.razorpay_payment_id,
                    'amount': int(refund.amount * 100),  # Convert to paise
                    'notes': {
                        'reason': refund.reason
                    }
                }
                
                razorpay_refund = client.refund.create(data=refund_data)
                
                refund.status = 'completed'
                refund.razorpay_refund_id = razorpay_refund['id']
                refund.processed_at = razorpay_refund['processed_at']
                refund.save()
                
                payment.status = 'refunded'
                payment.refund_date = refund.processed_at
                payment.save()
                
                messages.success(request, 'Refund processed successfully!')
                return redirect('payment_gateway:payment_detail', payment_id=payment.id)
                
            except Exception as e:
                messages.error(request, 'Failed to process refund. Please try again.')
    else:
        form = PaymentRefundForm(initial={'amount': payment.amount})
    
    return render(request, 'payment_gateway/refund_form.html', {
        'form': form,
        'payment': payment
    })

@csrf_exempt
def razorpay_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_X_RAZORPAY_SIGNATURE']
    
    try:
        client.utility.verify_webhook_signature(payload, sig_header, settings.RAZORPAY_WEBHOOK_SECRET)
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    
    if event['event'] == 'payment.captured':
        payment_data = event['payload']['payment']['entity']
        try:
            payment = Payment.objects.get(razorpay_order_id=payment_data['order_id'])
            payment.status = 'completed'
            payment.razorpay_payment_id = payment_data['id']
            payment.razorpay_signature = payment_data['signature']
            payment.save()
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)
    
    return JsonResponse({'status': 'success'})
