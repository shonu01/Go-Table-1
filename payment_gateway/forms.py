from django import forms
from .models import Payment, PaymentRefund

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method', 'amount', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={'readonly': True}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class PaymentRefundForm(forms.ModelForm):
    class Meta:
        model = PaymentRefund
        fields = ['amount', 'reason']
        widgets = {
            'amount': forms.NumberInput(attrs={'readonly': True}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

class StripePaymentForm(forms.Form):
    card_number = forms.CharField(
        max_length=16,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card Number'})
    )
    expiry_month = forms.CharField(
        max_length=2,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM'})
    )
    expiry_year = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'YYYY'})
    )
    cvv = forms.CharField(
        max_length=4,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CVV'})
    ) 