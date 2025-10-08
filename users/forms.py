from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    """A form for creating new users with email as the username and additional fields."""
    email = forms.EmailField(
        label='Email Address',
        max_length=254,
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'class': 'block w-full rounded-lg border-0 py-3 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-yas-primary sm:text-sm sm:leading-6 transition duration-150 ease-in-out',
            'placeholder': 'name@example.com',
            'aria-describedby': 'email-helper-text'
        }),
        help_text='<span id="email-helper-text" class="text-xs text-gray-500 mt-1">We\'ll use this email to send important updates.</span>'
    )
    first_name = forms.CharField(
        label='First Name',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-lg border-0 py-3 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-yas-primary sm:text-sm sm:leading-6 transition duration-150 ease-in-out',
            'placeholder': 'John',
            'autocomplete': 'given-name'
        })
    )
    last_name = forms.CharField(
        label='Last Name',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-lg border-0 py-3 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-yas-primary sm:text-sm sm:leading-6 transition duration-150 ease-in-out',
            'placeholder': 'Doe',
            'autocomplete': 'family-name'
        })
    )
    password1 = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'block w-full rounded-lg border-0 py-3 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-yas-primary sm:text-sm sm:leading-6 transition duration-150 ease-in-out',
            'placeholder': '••••••••',
            'aria-describedby': 'password-requirements'
        }),
        help_text='<div id="password-requirements" class="mt-2 space-y-1">'
                 '<p class="text-xs font-medium text-gray-500">Password requirements:</p>'
                 '<ul class="text-xs text-gray-500 list-disc pl-5 space-y-0.5">'
                 '<li>At least 8 characters</li>'
                 '<li>Can\'t be entirely numeric</li>'
                 '<li>Include letters, numbers, or symbols</li>'
                 '</ul>'
                 '</div>',
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'block w-full rounded-lg border-0 py-3 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-yas-primary sm:text-sm sm:leading-6 transition duration-150 ease-in-out',
            'placeholder': '••••••••',
            'aria-describedby': 'password-confirm-helper'
        }),
        strip=False,
        help_text='<span id="password-confirm-helper" class="text-xs text-gray-500">Please re-enter your password to confirm.</span>',
    )
    is_superuser = forms.BooleanField(
        label='',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 rounded border-gray-300 text-yas-primary focus:ring-yas-primary transition duration-150 ease-in-out',
            'aria-describedby': 'admin-helper'
        }),
        help_text='<span id="admin-helper" class="text-sm text-gray-500">Grant this user admin privileges</span>'
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'is_superuser')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.is_active = True
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    """A form for updating users with additional fields."""
    email = forms.EmailField(
        label='Email',
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-input'}),
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'is_active', 'is_superuser')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A user with that email already exists.")
        return email
