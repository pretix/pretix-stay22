import math
import time

import requests
from django import forms
from django.conf import settings
from django.core.validators import RegexValidator
from django.http import Http404, HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from pretix.base.forms import SettingsForm
from pretix.base.models import Event
from pretix.control.views.event import (
    EventSettingsFormView, EventSettingsViewMixin,
)


class Stay22SettingsForm(SettingsForm):
    stay22_aid = forms.CharField(
        label=_("Stay22 AID"),
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'pretix'})
    )
    stay22_embedlink = forms.CharField(
        label=_("Stay22 Embed Link"),
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'https://www.stay22.com/embed/myeventname'})
    )


class Stay22Settings(EventSettingsViewMixin, EventSettingsFormView):
    model = Event
    form_class = Stay22SettingsForm
    template_name = 'pretix_stay22/settings.html'
    permission = 'can_change_settings'

    def get_success_url(self) -> str:
        return reverse('plugins:pretix_stay22:settings', kwargs={
            'organizer': self.request.event.organizer.slug,
            'event': self.request.event.slug
        })
