from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from checkout.webhook_handler import Stripe_WH_Handler

import stripe
import json


@require_POST
@csrf_exempt
def webhook(request):
    """
    This deals with webhoosk sent from stripe and
    uses the handler to create functionailty from
    the webhook responses
    """
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = json.load(request.body)
    sig_header = request.headers.get["stripe-signature"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=wh_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(content=e, status=400)

    if event["type"] == "issuing_authorization.request":
        auth = event["data"]["object"]
        stripe.issuing.Authorization.approve(auth["id"])

    handler = Stripe_WH_Handler(request)

    event_map = {
        "payment_intent.succeeded": handler.handle_succeeded_payment,
        "payment_intent.payment_failed": handler.handle_failed_payment
    }

    event_type = event["type"]
    event_handler = event_map.get(event_type, handler.handle_event)

    response = event_handler(event)
    return response