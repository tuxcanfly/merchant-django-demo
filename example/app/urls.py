from django.conf.urls import *
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView


urlpatterns = patterns('app.views',
    url(r'^$', 'gateway', name='app_index'),
    url(r'^invoice$', 'invoice', name='app_invoice'),
    url(r'^gateway/(?P<gateway>[a-z0-9_]+)/$', 'gateway', name='app_gateway'),
    url(r'^integration/(?P<integration>[a-z0-9_]+)/$', 'integration', name='app_integration'),
)
