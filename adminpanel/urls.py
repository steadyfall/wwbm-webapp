from django.urls import path
from . import views as adminV

urlpatterns = [
    path("", adminV.AdminMainPage.as_view(), name="adminMainPage"),
    path("test/", adminV.testSite, name="test"),
    path("apps/<str:db>/", adminV.AdminListDB.as_view(), name="adminListDB"),
    path("logs/", adminV.ShowLogDB.as_view(), name="adminListLogs"),
    path(
        "apps/<str:db>/object/<pk>/",
        adminV.AdminDBObjectChange.as_view(),
        name="adminDBObject",
    ),
    path(
        "apps/<str:db>/create/",
        adminV.AdminDBObjectCreate.as_view(),
        name="adminDBObjectCreate",
    ),
    path(
        "apps/<str:db>/object/<pk>/delete/",
        adminV.AdminDBObjectDelete.as_view(),
        name="adminDBObjectDelete",
    ),
    path(
        "apps/<str:db>/object/<pk>/history/",
        adminV.AdminDBObjectHistory.as_view(),
        name="adminDBObjectHistory",
    ),
    path(
        "random-question/",
        adminV.GetQuestion.as_view(),
        name="getQuestionAPI",
    ),
    path(
        "add-questions/",
        adminV.AddQuestion.as_view(),
        name="addQuestionAPI",
    ),
]
