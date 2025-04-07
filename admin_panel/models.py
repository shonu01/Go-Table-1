from django.db import models
from accounts.models import CustomUser
from django.utils.translation import gettext_lazy as _

# Create your models here.

class AdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='admin_profile')
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Admin Profile')
        verbose_name_plural = _('Admin Profiles')

    def __str__(self):
        return f"{self.user.username}'s Admin Profile"
