from django import forms
from .models import Historicalevents
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import URLValidator
from urllib.parse import urlparse

class HistoricalEventForm(forms.ModelForm):
    eventdate = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DD'
            },
            format='%Y-%m-%d'
        ),
        input_formats=['%Y-%m-%d'],
        help_text='Enter the date when this historical event occurred'
    )

    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a descriptive title',
            'maxlength': '255'
        }),
        help_text='A clear, concise title for the historical event'
    )

    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Provide a detailed description of the event...'
        }),
        help_text='Describe the event, its significance, and its impact'
    )

    category = forms.ChoiceField(
        choices=Historicalevents.CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        help_text='Select the most appropriate category for this event'
    )

    location = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the location',
            'maxlength': '100'
        }),
        help_text='Where did this event take place?'
    )

    importance = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '10',
            'placeholder': '1-10'
        }),
        help_text='Rate the historical significance (1 = least important, 10 = most important)',
        min_value=1,
        max_value=10
    )

    source = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://example.com/article',
            'maxlength': '500'
        }),
        help_text='Provide a valid URL to a reliable source that verifies this event'
    )

    class Meta:
        model = Historicalevents
        fields = ['title', 'description', 'eventdate', 'category', 'location', 'importance', 'source']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

    def clean_eventdate(self):
        date = self.cleaned_data.get('eventdate')
        if date and date > timezone.now().date():
            raise ValidationError("Event date cannot be in the future")
        return date

    def clean_source(self):
        url = self.cleaned_data.get('source')
        if url:
            # Validate URL format
            try:
                URLValidator()(url)
            except ValidationError:
                raise ValidationError("Please enter a valid URL (e.g., https://example.com)")

            # Check if URL has a valid scheme
            parsed = urlparse(url)
            if parsed.scheme not in ['http', 'https']:
                raise ValidationError("URL must start with http:// or https://")

            # Additional validation could be added here
            # For example, checking against a list of trusted domains
            
        return url

class EventRejectionForm(forms.Form):
    reason = forms.CharField(
        label='Rejection Reason',
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'Please explain why this event submission is being rejected...'
        }),
        max_length=500,
        required=True,
        help_text='Provide clear feedback to help the submitter understand why their event was rejected'
    )