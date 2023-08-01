from django.urls import path
from . import views as adminV

urlpatterns = [
    path("", adminV.testSite, name="adminMainPage"),
    path("test/", adminV.testSite, name="test"),
    path("apps/<str:db>/", adminV.AdminListDB.as_view(), name="adminListDB"),
    path("apps/<str:db>/object/<pk>/", adminV.AdminDBObjectChange.as_view(), name="adminDBObject"),
    path("apps/<str:db>/create/", adminV.AdminDBObjectCreate.as_view(), name="adminDBObjectCreate"),
    path("apps/<str:db>/object/<pk>/delete/", adminV.AdminDBObjectDelete.as_view(), name="adminDBObjectDelete"),
]