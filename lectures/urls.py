from django.urls import path

from . import views

urlpatterns = [
    path("<int:lecture_id>/", views.lecture_detail, name="lecture_detail"),
]
