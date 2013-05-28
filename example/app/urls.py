from django.conf.urls import *
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView


urlpatterns = patterns('app.views',
    url(r'^$', 'index', name='app_index'),
    url(r'^invoice$', 'invoice', name='app_invoice'),
    url(r'^authorize/$', 'authorize', name='app_authorize'),
    url(r'^paypal/$', 'paypal', name='app_paypal'),
    url(r'^eway/$', 'eway', name='app_eway'),
    url(r'^braintree/$', 'braintree', name='app_braintree'),
    url(r'^stripe/$', 'stripe', name='app_stripe'),
    url(r'^paylane/$', 'paylane', name='app_paylane'),
    url(r'^beanstream/$', 'beanstream', name='app_beanstream'),
    url(r'^chargebee/$', 'chargebee', name='app_chargebee'),
    url(r'^we_pay/$', 'we_pay', name="app_we_pay"),
    url(r'^we_pay_redirect/$', 'we_pay_redirect', name="app_we_pay_redirect"),
    url(r'^we_pay_ipn/$', 'we_pay_ipn', name="app_we_pay_ipn"),
)
