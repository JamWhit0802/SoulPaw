from django.urls import path
from . import views

urlpatterns = [
    path("", views.intro, name="intro"),
    path("questionnaire/", views.questionnaire, name="questionnaire"),
]