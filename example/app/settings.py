import datetime
from django.conf import settings
from django.core.urlresolvers import reverse

from merchant.utils.paylane import (
    PaylanePaymentCustomer,
    PaylanePaymentCustomerAddress
)

from app.utils import randomword


HOST = getattr(settings, "HOST", "http://127.0.0.1")
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
            'x_card_num': '4007000000027',
            'x_exp_date': '01/20',
            'x_card_code': '100',
            'x_first_name': 'John',
            'x_last_name': 'Doe',
            'x_address': '100, Spooner Street, Springfield',
            'x_city': 'San Francisco',
            'x_state': 'California',
            'x_zip': '90210',
            'x_country': 'United States'
        },
    },

    'paypal': {
        'initial': {
            'amount_1': 1,
            'item_name_1': "Item 1",
            'amount_2': 2,
            'item_name_2': "Item 2",
            'invoice': datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
            'return_url': '{HOST}/invoice'.format(HOST=HOST),
            'cancel_return': '{HOST}/invoice'.format(HOST=HOST),
            'notify_url': '{HOST}/merchant/paypal/ipn'.format(HOST=HOST),
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
            'return_url': '{HOST}/invoice'.format(HOST=HOST)
        }
    },

    'amazon_fps': {
        'initial': {
            "transactionAmount": "100",
            "pipelineName": "SingleUse",
            "paymentReason": "Merchant Test",
            "paymentPage": "{HOST}/integration/amazon_fps/".format(HOST=HOST),
            "returnURL": '{HOST}/invoice'.format(HOST=HOST)
        }
    },

    'eway_au': {
        'post_init': lambda i: i.request_access_code(
            return_url="{HOST}:8000/invoice".format(HOST=HOST),
            customer={},
            payment={"total_amount": 100}
        )
    },

    "braintree_payments": {
        'initial': {
            "transaction": {
                "order_id": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
                "type": "sale",
                "options": {
                    "submit_for_settlement": True
                },
            },
            "site": "{HOST}:8000".format(HOST=HOST)
        }
    },

    "ogone_payments": {
        "initial": {
            'orderID': randomword(6),
            'currency': u'INR',
            'amount': u'10000',  # Rs. 100.00
            'language': 'en_US',
            'exceptionurl': "{HOST}:8000/ogone_notify_handler".format(HOST=HOST),
            'declineurl': "{HOST}:8000/ogone_notify_handler".format(HOST=HOST),
            'cancelurl': "{HOST}:8000/ogone_notify_handler".format(HOST=HOST),
            'accepturl': "{HOST}:8000/ogone_notify_handler".format(HOST=HOST),
        }
    }
}



