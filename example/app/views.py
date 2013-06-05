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
    'authorize_net_dpm': {
        'initial': {
            'x_amount': 1,
            'x_fp_sequence': datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
            'x_fp_timestamp': datetime.datetime.now().strftime('%s'),
            'x_recurring_bill': 'F',
        }
    },

    'paypal': {
        'initial': {
            'amount_1': 1,
            'item_name_1': "Item 1",
            'amount_2': 2,
            'item_name_2': "Item 2",
            'invoice': datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
            #'notify_url': reverse_lazy('app_offsite_paypal_done'),
            #'return_url': reverse_lazy(''),
            #'cancel_return': reverse_lazy('paypal-ipn'),
        }
    },

    'google_checkout': {
        'initial': {
            'items': [{
                        'amount': 1,
                        'name': 'name of the item',
                        'description': 'Item description',
                        'id': '999AXZ',
                        'currency': 'USD',
                        'quantity': 1,
                        "subscription": {
                        "type": "merchant",                     # valid choices is ["merchant", "google"]
                        "period": "YEARLY",                     # valid choices is ["DAILY", "WEEKLY", "SEMI_MONTHLY", "MONTHLY", "EVERY_TWO_MONTHS"," QUARTERLY", "YEARLY"]
                        "payments": [{
                                "maximum-charge": 9.99,         # Item amount must be "0.00"
                                "currency": "USD"
                        }]
                    },
                    "digital-content": {
                        "display-disposition": "OPTIMISTIC",    # valid choices is ['OPTIMISTIC', 'PESSIMISTIC']
                        "description": "Congratulations! Your subscription is being set up."
                    },
            }],
            'return_url': 'http://127.0.0.1:8000/invoice'
        }
    }
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
