from django.urls import path, include
from . import views as adminV

urlpatterns = [
    path("", adminV.testSite, name="adminMainPage"),
    path("test/", adminV.testSite, name="test"),
]