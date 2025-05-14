from django import forms
from .models import Booking
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from django.utils import timezone
from datetime import datetime, time, timedelta

class BookingForm(forms.ModelForm):
    # Define time slots from 11 AM to 11 PM with 30-minute intervals
    TIME_SLOTS = []
    start_time = time(11, 0)  # 11:00 AM
    end_time = time(23, 0)    # 11:00 PM
    current = datetime.combine(datetime.today(), start_time)
    end = datetime.combine(datetime.today(), end_time)
    
    while current <= end:
        time_slot = current.time()
        TIME_SLOTS.append(
            (time_slot.strftime('%H:%M'), time_slot.strftime('%I:%M %p'))
        )
        current += timedelta(minutes=30)

    booking_time = forms.ChoiceField(
        choices=TIME_SLOTS,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Choose your preferred dining time'
    )

    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number (e.g., 9876543210)'
        }),
        help_text='We may contact you on this number regarding your booking'
    )

    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        help_text='Select your preferred dining date'
    )

    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'party_size', 'seating_preference', 'special_requests', 'phone_number']
        widgets = {
            'party_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20'
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requests? (optional)'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('booking_date', css_class='form-group col-md-6'),
                Column('booking_time', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('party_size', css_class='form-group col-md-6'),
                Column('phone_number', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('seating_preference', css_class='form-group col-md-12'),
                css_class='form-row'
            ),
            'special_requests',
            Submit('submit', 'Make Reservation', css_class='btn btn-primary')
        )

    def clean_booking_date(self):
        date = self.cleaned_data.get('booking_date')
        if date < timezone.now().date():
            raise forms.ValidationError("You cannot book for a past date!")
        return date

    def clean_party_size(self):
        party_size = self.cleaned_data.get('party_size')
        if party_size < 1:
            raise forms.ValidationError("Party size must be at least 1!")
        if party_size > 20:
            raise forms.ValidationError("Party size cannot exceed 20!")
        return party_size

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # Remove any spaces or special characters
        phone = ''.join(filter(str.isdigit, phone))
        
        # Validate Indian phone number format
        if not phone.isdigit() or len(phone) != 10:
            raise forms.ValidationError("Please enter a valid 10-digit phone number")
        
        return phone