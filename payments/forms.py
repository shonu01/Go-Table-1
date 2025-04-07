from django import forms
from .models import Payment
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'transaction_id']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'transaction_id': forms.TextInput(attrs={'readonly': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('amount', css_class='form-group col-md-6 mb-0'),
                Column('payment_method', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'transaction_id',
            Submit('submit', 'Process Payment')
        )

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        payment_method = cleaned_data.get('payment_method')

        if amount and amount <= 0:
            raise forms.ValidationError('Payment amount must be greater than zero.')

        return cleaned_data 