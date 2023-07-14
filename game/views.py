from django.shortcuts import render
from game.models import *
import random


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
