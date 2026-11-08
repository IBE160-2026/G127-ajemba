from django.urls import include, path

from .views import home, lectures

urlpatterns = [
    path("", home, name="home"),
    path("lectures/", lectures, name="lectures"),
    path("lectures/", include("lectures.urls")),
    path("accounts/", include("accounts.urls")),
]
