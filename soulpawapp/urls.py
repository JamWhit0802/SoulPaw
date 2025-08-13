from django.urls import path
from . import views

urlpatterns = [
    path("", views.intro, name="intro"),
    path("questionnaire/", views.questionnaire, name="questionnaire"),
    path("dog-matches/", views.dog_matches, name="dog_matches"),
    path("dog-detail/<int:animal_id>/", views.dog_details, name="dog_detail"),
]