from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
import os
from django.conf import settings

class ReservationForm(forms.Form):
    name = forms.CharField(label='Jūsų vardas', max_length=100, initial='Test User' if settings.DEBUG else '')
    email = forms.EmailField(label='El. paštas', max_length=100, initial='test@example.com' if settings.DEBUG else '')
    phone = forms.CharField(label='Telefono numeris', max_length=100, initial='+37060000000' if settings.DEBUG else '')
    child_name = forms.CharField(label='Vaiko vardas', max_length=100, initial='Test Child' if settings.DEBUG else '')
    child_age = forms.IntegerField(label='Vaiko amžius mėnesiais', initial=12 if settings.DEBUG else None)
    comment = forms.CharField(label='Komentaras', widget=forms.Textarea, required=False, initial='Test comment' if settings.DEBUG else '')
    slot_start = forms.DateTimeField(widget=forms.HiddenInput())
    service = forms.ChoiceField(
        choices=[
            ('', 'Pasirinkite paslaugą'),
            ('Atvykimas į namus', 'Atvykimas į namus'),
            ('Online konsultacija', 'Online konsultacija'),
        ],
        label='Paslauga',
        initial='Online konsultacija' if settings.DEBUG else ''
    )
    city = forms.ChoiceField(
        choices=[
            ('', 'Pasirinkite miestą'),
            ('Klaipėda', 'Klaipėda'),
            ('Kretinga', 'Kretinga'),
            ('Palanga', 'Palanga'),
            ('Šventoji', 'Šventoji'),
        ],
        label='Miestas',
        required=False,
        initial='Klaipėda' if settings.DEBUG else ''
    )

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        city = cleaned_data.get('city')

        if service == 'Atvykimas į namus' and not city:
            self.add_error('city', 'Pasirinkite miestą')

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('name', css_class='form-control'),
            Field('email', css_class='form-control'),
            Field('phone', css_class='form-control'),
            Field('child_name', css_class='form-control'),
            Field('child_age', css_class='form-control'),
            Field('comment', css_class='form-control'),
            Field('slot_start'),
            Field('service', css_class='form-control'),
            Field('city', css_class='form-control'),
            Submit('submit', 'Rezervuoti', css_class='btn btn-primary')
        )