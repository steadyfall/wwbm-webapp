from django.shortcuts import render, redirect
from django.views.generic import View

from game.models import *
import random


# Testing pages

def mainPage(request):
    return render(request, "mainPage.html")

def rules(request):
    context = {"lifelines":Lifeline.objects.all()}
    return render(request, "rules.html", context)

def question(request):
    allOptions = [i.text for i in Question.objects.all()[345].incorrect_options.all()]
    allOptions.extend([Question.objects.all()[345].correct_option.text])
    random.shuffle(allOptions)
    p1 = allOptions[:2]
    p2 = allOptions[2:]

    context = {
        "question": Question.objects.all()[345].text,
        "options_part1": p1,
        "options_part2": p2,
    }
    return render(request, "question.html", context)


# Development pages

class MainPage(View):
    def get(self, request, *args, **kwargs):
        return render(request, "mainPage.html")
    
    def post(self, request, *args, **kwargs):
        if self.request.POST['startPlay'] == 'yes':
            new_session = Session.objects.create(session_user=self.request.user)
            return redirect("rules", session = new_session.session_id, permanent=True)
        return render(request, "mainPage.html")
    

class Rules(View):
    def get_sessionId(self):
        return self.kwargs['session']

    def get(self, request, *args, **kwargs):
        sessionId = self.get_sessionId()
        if Session.objects.filter(session_id = sessionId).exists():
            return render(request, "rules.html")
        return redirect("mainpage", permanent=True)
    
    def post(self, request, *args, **kwargs):
        sessionId = self.get_sessionId()
        sessionObj = Session.objects.get(session_id=sessionId)
        if self.request.POST['agreed'] == 'yes':
            sessionObj.agreedToRules = True
            sessionObj.save(update_fields=["agreedToRules"])
            print(sessionObj.agreedToRules)
            return render(request, "mainPage.html")
        sessionObj.delete()
        return redirect("mainpage", permanent=True) 