import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import RequestSite
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.views.generic import FormView, TemplateView

from merchant import CreditCard
from merchant.contrib.django.billing import get_gateway, get_integration
from merchant.gateway import CardNotSupported
from merchant.utils.paylane import (
    PaylanePaymentCustomer,
    PaylanePaymentCustomerAddress
)

from app.forms import CreditCardForm


GATEWAY_SETTINGS = {
    'authorize_net': {
        'initial': {
            'number': '4222222222222',
            'card_type': 'visa',
            'verification_value': '100'
        }
    },
    'eway': {
        'initial': {
            'number': '4444333322221111',
            'verification_value': '000'
        }
    },
    'braintree_payments': {
        'initial': {
            'number': '4111111111111111',
        }
    },
    'stripe': {
        'initial': {
            'number': '4242424242424242',
        }
    },
    'paylane': {
        'initial': {
            'number': '4111111111111111',
        },
        'kwargs': {
            'options': {
                'customer': PaylanePaymentCustomer(
                                name='John Doe',
                                email="test@example.com",
                                ip_address="127.0.0.1",
                                address=PaylanePaymentCustomerAddress(
                                            street_house='Av. 24 de Julho, 1117',
                                            city='Lisbon',
                                            zip_code='1700-000',
                                            country_code='PT',
                                         )
                            ),
                'product': {}
            }
        }
    },
    'beanstream': {
        'initial': {
            'number': '4030000010001234',
            'card_type': 'visa',
            'verification_value': '123'
        }
    },
    'chargebee': {
        'initial': {
            'number': '4111111111111111',
        },
        'args': ({"plan_id": "professional", "description": "Quick Purchase"},)
    }
}

INTEGRATION_SETTINGS = {
    'stripe': {
        'initial': {
            'amount': 1,
            'credit_card_number': '4222222222222',
            'credit_card_cvc': '100',
            'credit_card_expiration_month': '01',
            'credit_card_expiration_year': '2020'
        }
    },
}


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
        self.gateway = get_gateway(kwargs.get('gateway', 'authorize_net'), module_path="merchant.gateways")
        self.initial.update(GATEWAY_SETTINGS.get(self.gateway, {}).get('initial', {}))
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
        self.integration = get_integration(kwargs.get('integration', 'stripe'), module_path="app.integrations")
        from app.urls import urlpatterns
        urlpatterns += self.integration.urls
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
