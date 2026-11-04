from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.RecallLoginView.as_view(), name="login"),
    # LogoutView accepts POST only; a GET gets 405 and does not log out (AD-19.2).
    path("logout/", LogoutView.as_view(), name="logout"),
]
