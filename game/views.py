from django.shortcuts import render

QUESTION_LIMIT = len("What is the capital of Gujarat? What is the capital of Gujarat? What is the capital of ")
def home(request):
    return render(request, 'question.html')
