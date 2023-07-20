from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib import auth
from .validate import *


def register(request):
    error: str = "Data is invalid. Try again."
    if request.method == "POST":
        try:
            username: str = request.POST["username"]
            email: str = request.POST["email"]
            password: str = request.POST["password"]
            password2: str = request.POST["password2"]
        except KeyError:
            messages.error(request, error)
            return redirect("register")

        check: bool = (
            usernameValidator(username)
            and emailValidator(email)
            and passwordValidator(username, password)
            and confirmPassword(username, password, password2)
        )
        if check:
            if User.objects.filter(username=username).exists():
                messages.warning(request, "You already have an account.")
                return redirect("login")
            newuser = User.objects.create_user(
                username=username, email=email, password=password
            )
            messages.success(request, "Account successfully created!")
            return redirect("login")
        else:
            messages.error(request, error)
            return redirect("register")

    return render(request, "authentication/register.html")


def login(request):
    error: str = "Data is invalid. Try again."
    if request.method == "POST":
        try:
            username: str = request.POST["username"]
            password: str = request.POST["password"]
        except KeyError:
            messages.error(request, error)
            return redirect("login")

        check: bool = usernameValidator(username) and passwordValidator(
            username, password
        )
        if check:
            if not User.objects.filter(username=username).exists():
                messages.warning(request, "You don't have an account. Kindly register.")
                return redirect("register")
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('mainpage')
            else:
                messages.error(request, "Wrong password. Try again.")
                return redirect("login")
        else:
            messages.error(request, error)
            return redirect("login")

    return render(request, "authentication/signin.html")

def logout(request):
    if not request.user.is_authenticated:
        return redirect('mainpage')
    auth.logout(request)
    return render(request, "authentication/signout.html")
