from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe
from .models import Payment
from bookings.models import Booking
from .forms import PaymentForm
from django.core.paginator import Paginator

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_payment_intent(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    try:
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=int(booking.total_amount * 100),  # Convert to cents
            currency='usd',
            metadata={
                'booking_id': booking.id,
                'user_id': request.user.id
            }
        )
        
        return JsonResponse({
            'clientSecret': intent.client_secret,
            'publicKey': settings.STRIPE_PUBLIC_KEY
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=403)

@login_required
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Create payment record
    payment = Payment.objects.create(
        booking=booking,
        amount=booking.total_amount,
        payment_method='stripe',
        transaction_id=request.GET.get('payment_intent'),
        status='completed'
    )
    
    # Update booking status
    booking.status = 'confirmed'
    booking.save()
    
    messages.success(request, 'Payment processed successfully!')
    return redirect('bookings:detail', pk=booking.id)

@login_required
def payment_cancel(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    messages.warning(request, 'Payment was cancelled.')
    return redirect('bookings:detail', pk=booking.id)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        booking_id = payment_intent['metadata']['booking_id']
        user_id = payment_intent['metadata']['user_id']
        
        try:
            booking = Booking.objects.get(id=booking_id)
            payment = Payment.objects.get(booking=booking)
            payment.status = 'completed'
            payment.save()
            
            booking.status = 'confirmed'
            booking.save()
        except (Booking.DoesNotExist, Payment.DoesNotExist):
            return JsonResponse({'error': 'Booking or payment not found'}, status=404)
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        booking_id = payment_intent['metadata']['booking_id']
        user_id = payment_intent['metadata']['user_id']
        
        try:
            booking = Booking.objects.get(id=booking_id)
            payment = Payment.objects.get(booking=booking)
            payment.status = 'failed'
            payment.save()
        except (Booking.DoesNotExist, Payment.DoesNotExist):
            return JsonResponse({'error': 'Booking or payment not found'}, status=404)

    return JsonResponse({'status': 'success'})

@login_required
def payment_list(request):
    payments = Payment.objects.filter(booking__user=request.user).order_by('-created_at')
    paginator = Paginator(payments, 10)
    page = request.GET.get('page')
    payments = paginator.get_page(page)
    return render(request, 'payments/payment_list.html', {'payments': payments})

@login_required
def payment_detail(request, pk):
    payment = get_object_or_404(Payment, pk=pk, booking__user=request.user)
    return render(request, 'payments/payment_detail.html', {'payment': payment})

@login_required
def payment_create(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=request.user)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.save()
            messages.success(request, 'Payment processed successfully!')
            return redirect('payments:detail', pk=payment.pk)
    else:
        form = PaymentForm()
    return render(request, 'payments/payment_form.html', {'form': form, 'booking': booking})

@login_required
def payment_update(request, pk):
    payment = get_object_or_404(Payment, pk=pk, booking__user=request.user)
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payment updated successfully!')
            return redirect('payments:detail', pk=payment.pk)
    else:
        form = PaymentForm(instance=payment)
    return render(request, 'payments/payment_form.html', {'form': form, 'payment': payment})

@login_required
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk, booking__user=request.user)
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Payment deleted successfully!')
        return redirect('payments:list')
    return render(request, 'payments/payment_confirm_delete.html', {'payment': payment})
