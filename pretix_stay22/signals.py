from datetime import timedelta
from urllib.parse import urlparse, urlencode

from django.conf import settings
from django.contrib.staticfiles import finders
from django.dispatch import receiver
from django.http import HttpRequest, HttpResponse
from django.template.loader import get_template
from django.urls import resolve, reverse
from django.utils.translation import gettext_lazy as _

from pretix.base.middleware import _parse_csp, _merge_csp, _render_csp
from pretix.base.models import Order, Event
from pretix.control.signals import nav_event_settings
from pretix.presale.signals import order_info, process_response, sass_postamble


def stay22_params(event, ev, ev_last, order):
    p = {
        'aid': event.settings.stay22_aid or 'pretix-{}{}'.format(urlparse(settings.SITE_URL).hostname, event.pk),
        'maincolor': event.settings.primary_color[1:],
        'venue': str(ev.location).replace('\n', ', '),
        'ljs': order.locale[:2],

    }
    if ev.geo_lat and ev.geo_lon:
        p['lat'] = str(ev.geo_lat)
        p['lng'] = str(ev.geo_lon)
    else:
        p['address'] = ev.location.localize('en').replace('\n', ', ').strip()

    df = ev.date_from.astimezone(event.timezone)
    p['checkin'] = (df - timedelta(days=1)).date().isoformat() if df.hour < 12 else df.date().isoformat()
    dt = max(df + timedelta(days=1), (ev_last.date_to or ev_last.date_from)).astimezone(event.timezone)
    p['checkout'] = (dt + timedelta(days=1)).date().isoformat() if dt.hour > 12 else dt.date().isoformat()

    return p


@receiver(order_info, dispatch_uid="stay22_order_info")
def order_info(sender: Event, order: Order, **kwargs):
    subevents = {op.subevent for op in order.positions.all()}
    if sender.settings.stay22_embedlink:
        ctx = {
            'url': sender.settings.stay22_embedlink
        }
    else:
        ctx = {
            'url': 'https://www.stay22.com/embed/gm?{}'.format(urlencode(stay22_params(
                sender,
                min(subevents, key=lambda s: s.date_from) if sender.has_subevents else sender,
                max(subevents, key=lambda s: s.date_to or s.date_from) if sender.has_subevents else sender,
                order
            )))
        }
    ctx['click_to_load'] = sender.settings.get("cookie_consent")
    ctx['privacy_url'] = sender.settings.get("privacy_url")
    template = get_template('pretix_stay22/order_info.html')
    return template.render(ctx)


@receiver(signal=process_response, dispatch_uid="stay22_middleware_resp")
def signal_process_response(sender, request: HttpRequest, response: HttpResponse, **kwargs):
    if 'Content-Security-Policy' in response:
        h = _parse_csp(response['Content-Security-Policy'])
    else:
        h = {}

    _merge_csp(h, {
        'frame-src': ['https://www.stay22.com'],
    })

    if h:
        response['Content-Security-Policy'] = _render_csp(h)
    return response


@receiver(sass_postamble, dispatch_uid="stay22_sass_postamble")
def r_sass_postamble(sender, filename, **kwargs):
    if filename == "main.scss":
        with open(finders.find('pretix_stay22/postamble.scss'), 'r') as fp:
            return fp.read()
    return ""


@receiver(nav_event_settings, dispatch_uid='stay22_nav')
def navbar_info(sender, request, **kwargs):
    url = resolve(request.path_info)
    if not request.user.has_event_permission(request.organizer, request.event, 'can_change_event_settings',
                                             request=request):
        return []
    return [{
        'label': _('Stay22'),
        'icon': 'house',
        'url': reverse('plugins:pretix_stay22:settings', kwargs={
            'event': request.event.slug,
            'organizer': request.organizer.slug,
        }),
        'active': url.namespace == 'plugins:pretix_stay22',
    }]
