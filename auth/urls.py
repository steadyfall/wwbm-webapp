from django.urls import path
from . import views as authApp

urlpatterns = [
    path("login/", authApp.login, name="login"),
    path("logout/", authApp.logout, name="logout"),
    path("register/", authApp.register, name="register"),
    path("admin-login/", authApp.adminlogin, name="adminLogin"),
    path("admin-logout/", authApp.adminlogout, name="adminLogout"),
]
