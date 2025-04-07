from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from restaurants.models import Restaurant

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField(default=timezone.now)
    booking_time = models.TimeField(default=timezone.now)
    party_size = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)], default=2)
    special_requests = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-booking_date', '-booking_time']
        
    def __str__(self):
        return f"{self.user.username}'s booking at {self.restaurant.name} on {self.booking_date} at {self.booking_time}"
        
