from django.urls import path
from . import views as adminV

urlpatterns = [
    path("", adminV.testSite, name="adminMainPage"),
    path("test/", adminV.testSite, name="test"),
    path("apps/<str:db>/", adminV.AdminListDB.as_view(), name="adminListDB"),
    path("apps/<str:db>/object/<pk>/", adminV.testSite, name="adminDBObject"),
    path("apps/<str:db>/object/create/", adminV.testSite, name="adminDBObjectCreate"),
    path("apps/<str:db>/object/<pk>/delete/", adminV.testSite, name="adminDBObjectDelete"),
]