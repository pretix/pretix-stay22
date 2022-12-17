from django.urls import path

from .views import Stay22Settings

urlpatterns = [
    path('control/event/<str:organizer>/<str:event>/stay22/settings',
        Stay22Settings.as_view(), name='settings'),
]
