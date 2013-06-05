from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from merchant.contrib.django.billing.integrations.stripe_integration import StripeIntegration as Integration


class StripeIntegration(Integration):

    def transaction(self, request):
        response = self.gateway.purchase(100, request.POST["stripeToken"])
        if response["status"]:
            messages.success(request, "Transcation successful")
        else:
            messages.error(request, "Transcation declined")
            return redirect(request.path)
        return redirect("app_invoice")
