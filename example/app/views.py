import datetime

from django.conf import settings
from django.contrib.sites.models import RequestSite
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext

from merchant import CreditCard, get_gateway, get_integration
from merchant.gateway import CardNotSupported
from merchant.utils.paylane import (
    PaylanePaymentCustomer,
    PaylanePaymentCustomerAddress
)

from app.forms import CreditCardForm


def index(request, gateway=None):
    return authorize(request)


def authorize(request):
    amount = 1
    response = None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("authorize_net")
            try:
                merchant.validate_card(credit_card)
            except CardNotSupported:
                response = "Credit Card Not Supported"
            response = merchant.purchase(amount, credit_card)
            #response = merchant.recurring(amount, credit_card)
    else:
        form = CreditCardForm(initial={'number': '4222222222222'})
    return render(request, 'app/index.html', {'form': form,
                                              'amount': amount,
                                              'response': response,
                                              'title': 'Authorize'})


def paypal(request):
    amount = 1
    response = None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("pay_pal")
            try:
                merchant.validate_card(credit_card)
            except CardNotSupported:
                response = "Credit Card Not Supported"
            # response = merchant.purchase(amount, credit_card, options={'request': request})
            response = merchant.recurring(amount, credit_card, options={'request': request})
    else:
        form = CreditCardForm(initial={'number': '4797503429879309',
                                       'verification_value': '037',
                                       'month': 1,
                                       'year': 2019,
                                       'card_type': 'visa'})
    return render(request, 'app/index.html', {'form': form,
                                              'amount': amount,
                                              'response': response,
                                              'title': 'Paypal'})


def eway(request):
    amount = 1
    response = None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("eway")
            try:
                merchant.validate_card(credit_card)
            except CardNotSupported:
                response = "Credit Card Not Supported"
            merchant.contrib.django.billing_address = {'salutation': 'Mr.',
                               'address1': 'test',
                               'address2': ' street',
                               'city': 'Sydney',
                               'state': 'NSW',
                               'company': 'Test Company',
                               'zip': '2000',
                               'country': 'au',
                               'email': 'test@example.com',
                               'fax': '0267720000',
                               'phone': '0267720000',
                               'mobile': '0404085992',
                               'customer_ref': 'REF100',
                               'job_desc': 'test',
                               'comments': 'any',
                               'url': 'http://www.google.com.au',
                               }
            response = merchant.purchase(amount, credit_card, options={'request': request, 'merchant.contrib.django.billing_address': merchant.contrib.django.billing_address})
    else:
        form = CreditCardForm(initial={'number':'4444333322221111',
                                       'verification_value': '000',
                                       'month': 7,
                                       'year': 2012})
    return render(request, 'app/index.html', {'form': form,
                                              'amount': amount,
                                              'response': response,
                                              'title': 'Eway'})

def braintree(request):
    amount = 1
    response = None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("braintree_payments")
            try:
                merchant.validate_card(credit_card)
            except CardNotSupported:
                response = "Credit Card Not Supported"
            response = merchant.purchase(amount, credit_card)
    else:
        form = CreditCardForm(initial={'number':'4111111111111111'})
    return render(request, 'app/index.html', {'form': form,
                                              'amount': amount,
                                              'response': response,
                                              'title': 'Braintree Payments (S2S)'})
def stripe(request):
    amount = 1
    response= None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("stripe")
            response = merchant.purchase(amount,credit_card)
    else:
        form = CreditCardForm(initial={'number':'4242424242424242'})
    return render(request, 'app/index.html',{'form': form,
                                             'amount':amount,
                                             'response':response,
                                             'title':'Stripe Payment'})


def paylane(request):
    amount = 1
    response= None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("paylane")
            customer = PaylanePaymentCustomer()
            customer.name = "%s %s" %(data['first_name'], data['last_name'])
            customer.email = "testuser@example.com"
            customer.ip_address = "127.0.0.1"
            options = {}
            address = PaylanePaymentCustomerAddress()
            address.street_house = 'Av. 24 de Julho, 1117'
            address.city = 'Lisbon'
            address.zip_code = '1700-000'
            address.country_code = 'PT'
            customer.address = address
            options['customer'] = customer
            options['product'] = {}
            response = merchant.purchase(amount, credit_card, options = options)
    else:
        form = CreditCardForm(initial={'number':'4111111111111111'})
    return render(request, 'app/index.html', {'form': form,
                                              'amount':amount,
                                              'response':response,
                                              'title':'Paylane Gateway'})


def we_pay(request):
    wp = get_gateway("we_pay")
    form = None
    amount = 10
    response = wp.purchase(10, None, {
            "description": "Test Merchant Description",
            "type": "SERVICE",
            "redirect_uri": request.build_absolute_uri(reverse('app_we_pay_redirect'))
            })
    if response["status"] == "SUCCESS":
        return HttpResponseRedirect(response["response"]["checkout_uri"])
    return render(request, 'app/index.html', {'form': form,
                                              'amount':amount,
                                              'response':response,
                                              'title':'WePay Payment'})

def we_pay_redirect(request):
    checkout_id = request.GET.get("checkout_id", None)
    return render(request, 'app/we_pay_success.html', {"checkout_id": checkout_id})


def we_pay_ipn(request):
    # Just a dummy view for now.
    return render(request, 'app/index.html', {})


def beanstream(request):
    amount = 1
    response = None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("beanstream")
            response = merchant.purchase(amount, credit_card,
                                         {"merchant.contrib.django.billing_address": {
                        "name": "%s %s" % (data["first_name"], data["last_name"]),
                        # below are hardcoded just for the sake of the example
                        # you can make these optional by toggling the customer name
                        # and address in the account dashboard.
                        "email": "test@example.com",
                        "phone": "555-555-555-555",
                        "address1": "Addr1",
                        "address2": "Addr2",
                        "city": "Hyd",
                        "state": "AP",
                        "country": "IN"
                        }
                                          })
    else:
        form = CreditCardForm(initial={'number':'4030000010001234',
                                       'card_type': 'visa',
                                       'verification_value': 123})
    return render(request, 'app/index.html',{'form': form,
                                             'amount': amount,
                                             'response': response,
                                             'title': 'Beanstream'})

def chargebee(request):
    amount = 1
    response = None
    if request.method == 'POST':
        form = CreditCardForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            credit_card = CreditCard(**data)
            merchant = get_gateway("chargebee")
            response = merchant.purchase(amount, credit_card,
                                         {"plan_id": "professional",
                                          "description": "Quick Purchase"})
    else:
        form = CreditCardForm(initial={'number':'4111111111111111',
                                       'card_type': 'visa',
                                       'verification_value': 100})
    return render(request, 'app/index.html',{'form': form,
                                             'amount': amount,
                                             'response': response,
                                             'title': 'Chargebee'})
