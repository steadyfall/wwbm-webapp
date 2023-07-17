from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views as game_views

urlpatterns = [
    path('', game_views.MainPage.as_view(), name="mainpage"),
    path('game/<str:session>/rules/', game_views.Rules.as_view(), name="rules"),
    path('game/<str:session>/question/<int:level>/', game_views.QuestionInGame.as_view(), name="question"),
    path('game/<str:session>/question/<int:level>/correct', game_views.sample, name="correct")
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
