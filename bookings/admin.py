from django.contrib import admin
from .models import Booking
from payments.models import Payment

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'restaurant', 'booking_date', 'booking_time', 'party_size', 'status')
    list_filter = ('status', 'booking_date', 'restaurant')
    search_fields = ('user__email', 'restaurant__name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'status', 'payment_method')
    list_filter = ('status', 'payment_method')
    search_fields = ('booking__user__email', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
