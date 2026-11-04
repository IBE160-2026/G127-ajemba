from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import LoginView
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render

from .forms import EMAIL_IN_USE_MESSAGE, LoginForm, RegisterForm


class RecallLoginView(LoginView):
    """Django's LoginView. It checks "next" with url_has_allowed_host_and_scheme and falls
    back to LOGIN_REDIRECT_URL (the home page) when "next" points to another site (AD-7)."""

    authentication_form = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


def register(request):
    if request.user.is_authenticated:
        return redirect("lectures")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                user = get_user_model().objects.create_user(
                    email=form.cleaned_data["email"], password=form.cleaned_data["password"]
                )
        except IntegrityError:  # two registrations for one email at the same moment
            form.add_error("email", EMAIL_IN_USE_MESSAGE)
        else:
            login(request, user)
            return redirect("lectures")
    return render(request, "accounts/register.html", {"form": form})
