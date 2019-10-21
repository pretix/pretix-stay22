from django.conf.urls import url

from .views import Stay22Settings

urlpatterns = [
    url(r'^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/stay22/settings$',
        Stay22Settings.as_view(), name='settings'),
]
