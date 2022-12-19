from django.utils.translation import gettext_lazy
from . import __version__
try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")


class PluginApp(PluginConfig):
    default = True
    name = 'pretix_stay22'
    verbose_name = 'Stay22 Hotel map'

    class PretixPluginMeta:
        name = gettext_lazy('Stay22 Hotel map')
        author = 'Raphael Michel'
        category = 'INTEGRATION'
        picture = "pretix_stay22/logo.svg"
        description = gettext_lazy('Integrate the Stay22 hotel map into your shop')
        visible = True
        version = __version__
        compatibility = "pretix>=3.2.999"

    def ready(self):
        from . import signals  # NOQA


