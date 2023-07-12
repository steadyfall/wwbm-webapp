from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views as game_views

urlpatterns = [
    path('', game_views.home, name="home"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
