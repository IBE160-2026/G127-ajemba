from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from . import throttle
from .managers import normalise_email

EMAIL_IN_USE_MESSAGE = "This email is already in use. Log in, or use another."


class RegisterForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def clean_email(self):
        email = normalise_email(self.cleaned_data["email"])
        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError(EMAIL_IN_USE_MESSAGE, code="email_in_use")
        return email

    def clean(self):
        cleaned = super().clean()
        email, password = cleaned.get("email"), cleaned.get("password")
        if email and password:
            # Django's default validators; their own plain messages are shown (AD-7).
            try:
                validate_password(password, user=get_user_model()(email=email))
            except ValidationError as error:
                self.add_error("password", error)
        return cleaned


class LoginForm(AuthenticationForm):
    """Django's log-in form, plus the failure limit and a normalised email."""

    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email"}))
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def clean_username(self):
        return normalise_email(self.cleaned_data["username"])

    def clean(self):
        email = self.cleaned_data.get("username")
        address = throttle.client_address(self.request)
        if email and throttle.is_blocked(email, address):
            raise ValidationError(throttle.BLOCKED_MESSAGE, code="throttled")
        try:
            cleaned = super().clean()
        except ValidationError:
            if email:
                throttle.record_failure(email, address)
            raise
        if email and self.get_user() is not None:
            throttle.clear(email, address)
        return cleaned
