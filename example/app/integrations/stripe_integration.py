from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from merchant.contrib.django.billing.integrations.stripe_integration import StripeIntegration as Integration


class StripeIntegration(Integration):

    def transaction(self, request):
        resp = self.gateway.purchase(100, request.POST["stripeToken"])
        return redirect("app_invoice")
