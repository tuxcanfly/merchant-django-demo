from django.contrib import messages
from django.contrib.sites.models import RequestSite
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.views.generic import FormView, TemplateView

from merchant import CreditCard
from merchant.contrib.django.billing import get_gateway, get_integration
from merchant.gateway import CardNotSupported

from app.forms import CreditCardForm
from app.settings import GATEWAY_SETTINGS, INTEGRATION_SETTINGS, HOST


class PaymentGatewayFormView(FormView):

    form_class = CreditCardForm
    initial = {
        'first_name': 'John',
        'last_name': 'Doe',
        'month': '06',
        'year': '2020',
        'card_type': 'visa',
        'verification_value': '000'
    }
    success_url = reverse_lazy("app_invoice")
    template_name = 'app/gateway.html'

    amount = 1

    def dispatch(self, *args, **kwargs):
        gateway_key = kwargs.get("gateway", "authorize_net")
        self.gateway = get_gateway(gateway_key, module_path="merchant.gateways")
        if gateway_key in GATEWAY_SETTINGS and "initial" in GATEWAY_SETTINGS[gateway_key]:
            self.initial.update(GATEWAY_SETTINGS[gateway_key]["initial"])
        return super(PaymentGatewayFormView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PaymentGatewayFormView, self).get_context_data(**kwargs)
        context.update({
            'gateway': self.gateway,
            'amount': self.amount
        })
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        credit_card = CreditCard(**data)
        try:
            self.gateway.validate_card(credit_card)
            args = GATEWAY_SETTINGS.get(self.gateway, {}).get('args', ())
            kwargs = GATEWAY_SETTINGS.get(self.gateway, {}).get('kwargs', {})
            response = self.gateway.purchase(self.amount, credit_card, *args, **kwargs)
            if response["status"]:
                messages.success(self.request, "Transcation successful")
            else:
                messages.error(self.request, "Transcation declined")
                return self.form_invalid(form)
        except CardNotSupported:
            messages.error(self.request, "Credit Card Not Supported")
            return self.form_invalid(form)
        return super(PaymentGatewayFormView, self).form_valid(form)


class PaymentIntegrationFormView(TemplateView):
    template_name = 'app/integration.html'

    def dispatch(self, *args, **kwargs):
        integration_key = kwargs.get('integration', 'stripe')
        self.integration = get_integration(integration_key, module_path="app.integrations")

        if integration_key in INTEGRATION_SETTINGS and "post_init" in INTEGRATION_SETTINGS[integration_key]:
            print INTEGRATION_SETTINGS[integration_key]["post_init"](self.integration)

        #  monkey see, monkey patch
        from app.urls import urlpatterns
        urlpatterns += self.integration.urls

        initial = {}
        if integration_key in INTEGRATION_SETTINGS and "initial" in INTEGRATION_SETTINGS[integration_key]:
            initial.update(INTEGRATION_SETTINGS[integration_key]["initial"])
        self.integration.add_fields(initial)
        return super(PaymentIntegrationFormView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(PaymentIntegrationFormView, self).get_context_data(**kwargs)
        context.update({
            'integration': self.integration,
        })
        return context


class InvoiceView(TemplateView):
    template_name = 'app/invoice.html'


gateway = PaymentGatewayFormView.as_view()
integration = PaymentIntegrationFormView.as_view()
invoice = InvoiceView.as_view()
