import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.sites.models import RequestSite
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
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


class MerchantFormView(FormView):

    form_class = CreditCardForm
    initial = {
        'first_name': 'John',
        'last_name': 'Doe',
        'month': '06',
        'year': '2020',
        'card_type': 'visa',
        'verification_value': '000'
    }
    success_url = '/invoice'
    template_name = 'app/index.html'

    amount = 1

    def dispatch(self, *args, **kwargs):
        self.gateway = kwargs.get('gateway', 'authorize_net')
        self.initial.update(GATEWAY_SETTINGS.get(self.gateway, {}).get('initial', {}))
        return super(MerchantFormView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MerchantFormView, self).get_context_data(**kwargs)
        context.update({
            'title': self.gateway,
            'amount': self.amount
        })
        return context

    def form_valid(self, form):
        data = form.cleaned_data
        credit_card = CreditCard(**data)
        merchant = get_gateway(self.gateway)
        try:
            merchant.validate_card(credit_card)
            args = GATEWAY_SETTINGS.get(self.gateway, {}).get('args', ())
            kwargs = GATEWAY_SETTINGS.get(self.gateway, {}).get('kwargs', {})
            merchant.purchase(self.amount, credit_card, *args, **kwargs)
            messages.success(self.request, "Transcation successful")
        except CardNotSupported:
            messages.error(self.request, "Credit Card Not Supported")
            return self.form_invalid(form)
        return super(MerchantFormView, self).form_valid(form)


class MerchantInvoiceView(TemplateView):
    template_name = 'app/invoice.html'


payment = MerchantFormView.as_view()
invoice = MerchantInvoiceView.as_view()
