from django import forms
from django.forms import ModelForm
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Lead, Feedback, Interaction, Customer
from .quick_services import QuickServiceRequest


class LeadUpdateForm(ModelForm):
    """Form for updating lead status and notes."""
    class Meta:
        model = Lead
        fields = ['status', 'lead_type', 'notes', 'expected_close_date', 'value']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select',
                'hx-post': '.',
                'hx-trigger': 'change',
                'hx-target': '#lead-details',
            }),
            'lead_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add notes about this lead...',
            }),
            'expected_close_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': timezone.now().date().isoformat(),
            }),
            'value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estimated value',
                'min': 0,
                'step': '0.01',
            }),
        }
        help_texts = {
            'status': 'Current status of the lead in the sales pipeline.',
            'lead_type': 'Type of lead based on the buying timeline.',
            'notes': 'Any additional information about this lead.',
            'expected_close_date': 'When do you expect to close this deal?',
            'value': 'Estimated value of this opportunity.',
        }

    def clean_expected_close_date(self):
        close_date = self.cleaned_data.get('expected_close_date')
        if close_date and close_date < timezone.now().date():
            raise ValidationError("Close date cannot be in the past.")
        return close_date

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        
        # If status is closed_won or closed_lost, ensure close date is set
        if status in ['closed_won', 'closed_lost'] and not cleaned_data.get('expected_close_date'):
            cleaned_data['expected_close_date'] = timezone.now().date()
            
        return cleaned_data


class FeedbackForm(ModelForm):
    """Form for adding customer feedback."""
    class Meta:
        model = Feedback
        fields = ['rating', 'comment', 'is_resolved', 'resolution_notes']
        widgets = {
            'rating': forms.RadioSelect(
                choices=[(i, '★' * i + '☆' * (5 - i)) for i in range(1, 6)],
                attrs={
                    'class': 'rating-radio',
                }
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your feedback...',
            }),
            'is_resolved': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'resolution_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'How was this feedback addressed?',
            }),
        }
        help_texts = {
            'rating': 'Rate your experience (1-5 stars)',
            'comment': 'Your feedback helps us improve our service.',
            'is_resolved': 'Check if this feedback has been resolved.',
            'resolution_notes': 'Notes on how this feedback was addressed.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show resolution fields if editing existing feedback
        if not self.instance.pk:
            self.fields['is_resolved'].widget = forms.HiddenInput()
            self.fields['resolution_notes'].widget = forms.HiddenInput()


class InteractionForm(ModelForm):
    """Form for recording customer interactions."""
    class Meta:
        model = Interaction
        fields = ['action_type', 'details', 'notes', 'is_completed']
        widgets = {
            'action_type': forms.Select(
                attrs={
                    'class': 'form-select',
                },
                choices=Interaction.ACTION_TYPES
            ),
            'details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter any additional details in JSON format (optional)...',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter details of the interaction...',
            }),
            'is_completed': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        help_texts = {
            'action_type': 'Type of interaction (call, meeting, email, purchase, etc.)',
            'details': 'Additional details in JSON format (e.g., {"duration": 30, "topic": "Product Demo"})',
            'notes': 'Details about what was discussed or accomplished.',
            'is_completed': 'Check if this interaction is complete.',
        }

    def clean_details(self):
        details = self.cleaned_data.get('details', '').strip()
        if not details:
            return {}
        
        try:
            import json
            # If details is already a dict (from model instance), return as is
            if isinstance(details, dict):
                return details
            # Otherwise try to parse as JSON
            return json.loads(details)
        except json.JSONDecodeError:
            raise ValidationError("Please enter valid JSON format for details.")


class CustomerForm(ModelForm):
    """Form for adding/editing customer information."""
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address', 'visit_reason', 'notes', 'assigned_agent']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number with country code',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Physical address',
            }),
            'visit_reason': forms.Select(attrs={
                'class': 'form-select',
            }),
            'assigned_agent': forms.Select(attrs={
                'class': 'form-select',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Any additional notes about this customer...',
            }),
        }
        help_texts = {
            'phone': 'Include country code (e.g., +255 for Tanzania)',
            'visit_reason': 'Primary reason for the customer\'s visit.',
            'assigned_agent': 'Agent responsible for this customer.',
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Basic phone number validation
        if not phone.replace('+', '').isdigit():
            raise ValidationError("Phone number can only contain numbers and '+'.")
        return phone
