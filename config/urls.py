from django.urls import include, path

from .views import home, lecture_status, lectures

urlpatterns = [
    path("", home, name="home"),
    path("lectures/", lectures, name="lectures"),
    path("status/lecture/<int:lecture_id>/", lecture_status, name="lecture_status"),
    path("lectures/", include("lectures.urls")),
    path("accounts/", include("accounts.urls")),
]
