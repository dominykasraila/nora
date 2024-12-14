from django import forms

class EventForm(forms.Form):
    summary = forms.CharField(label='Event Summary', max_length=100)
    start_time = forms.DateTimeField(
        label='Start Time',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )
    end_time = forms.DateTimeField(
        label='End Time',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
    )