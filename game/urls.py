from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views as game_views

urlpatterns = [
    path("tester/", game_views.pageChecker, name="tester"),
    path("", game_views.MainPage.as_view(), name="mainpage"),
    path("about/", game_views.About.as_view(), name="about"),
    path("leaderboard/", game_views.Leaderboard.as_view(), name="leaderboard"),
    path("scores/", game_views.ScoreBoard.as_view(), name="scores"),
    path("game/<str:session>/rules/", game_views.Rules.as_view(), name="rules"),
    path(
        "game/<str:session>/question/<int:level>/",
        game_views.QuestionInGame.as_view(),
        name="question",
    ),
    path(
        "game/<str:session>/question/<int:level>/<str:status>/",
        game_views.BetweenQuestion.as_view(),
        name="statusAfterQn",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
