from django import forms
from .models import Restaurant, Table, MenuItem, Review
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'description', 'address', 'city', 'state', 'country', 
                 'postal_code', 'phone', 'email', 'website', 'opening_time', 
                 'closing_time', 'cuisine_type', 'price_range', 'image', 'is_featured']
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('cuisine_type', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'description',
            Row(
                Column('address', css_class='form-group col-md-6 mb-0'),
                Column('city', css_class='form-group col-md-3 mb-0'),
                Column('state', css_class='form-group col-md-3 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('country', css_class='form-group col-md-4 mb-0'),
                Column('postal_code', css_class='form-group col-md-4 mb-0'),
                Column('phone', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-0'),
                Column('website', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('opening_time', css_class='form-group col-md-6 mb-0'),
                Column('closing_time', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('price_range', css_class='form-group col-md-6 mb-0'),
                Column('image', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Save Restaurant')
        )

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['table_number', 'capacity', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('table_number', css_class='form-group col-md-4 mb-0'),
                Column('capacity', css_class='form-group col-md-4 mb-0'),
                Column('status', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Save Table')
        )

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'category', 'image', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('category', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'description',
            Row(
                Column('price', css_class='form-group col-md-6 mb-0'),
                Column('image', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Field('is_available', css_class='form-check-input'),
            Submit('submit', 'Save Menu Item')
        )

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'rating',
            'comment',
            Submit('submit', 'Submit Review')
        ) 