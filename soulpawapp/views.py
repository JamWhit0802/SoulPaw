from django.shortcuts import render, HttpResponse
from .models import TodoItem
def intro(request):
    #return HttpResponse("Welcome to SoulPaw App!")
    return render(request, "intro.html")

def questionnaire(request):
    #return HttpResponse("This is the questionnaire page.")
    return render(request, "questionnaire.html")