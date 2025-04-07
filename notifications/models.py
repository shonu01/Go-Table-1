from django.db import models
from django.conf import settings
from bookings.models import Booking

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('booking_confirmation', 'Booking Confirmation'),
        ('booking_reminder', 'Booking Reminder'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('payment_success', 'Payment Success'),
        ('payment_failed', 'Payment Failed'),
        ('review_reminder', 'Review Reminder'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} for {self.user.email}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()
