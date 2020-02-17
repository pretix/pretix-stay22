from django.utils.translation import ugettext_lazy
try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    name = 'pretix_stay22'
    verbose_name = 'Stay22 Hotel map'

    class PretixPluginMeta:
        name = ugettext_lazy('Stay22 Hotel map')
        author = 'Raphael Michel'
        category = 'INTEGRATION'
        description = ugettext_lazy('This plugin allows to integrate the Stay22 hotel map into your pretix shop')
        visible = True
        version = '1.0.1'
        compatibility = "pretix>=3.2.999"

    def ready(self):
        from . import signals  # NOQA


default_app_config = 'pretix_stay22.PluginApp'
