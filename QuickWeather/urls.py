from django.contrib import admin
from django.urls import path
from weather.views import weather_view, clear_history


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', weather_view, name='weather'),
    path('clear-history/', clear_history, name='clear_history'),
]
