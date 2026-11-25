from django.urls import path

from . import views

urlpatterns = [
    path("upload/", views.upload, name="upload"),
    path("<int:lecture_id>/", views.lecture_detail, name="lecture_detail"),
    path("<int:lecture_id>/retry/", views.retry, name="lecture_retry"),
]
