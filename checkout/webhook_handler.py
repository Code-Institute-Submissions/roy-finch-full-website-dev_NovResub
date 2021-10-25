from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Order, Order_Items
from products.models import Product
from profiles.models import UserProfile

import json
import time


class Stripe_WH_Handler:
    """ This will deal with webhooks for stripe """

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        customer_email = order.email
        subject = render_to_string(
            'checkout/confirmation_email_temps/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails_temps/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [customer_email]
        )

    def handle_event(self, event):
        return HttpResponse(content=f"Webhook recieved: {event['type']}",
                            status=200)

    def handle_succeeded_payment(self, event):
        intent = event.data.object
        pid = intent.id
        basket = intent.metadata.basket
        save_order = intent.metadata.save_order

        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping_details
        grand_total = round(intent.charges.data[0].amount/100, 2)

        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        profile = None
        username = intent.metadata.username
        if username != "AnonymousUser":
            profile = UserProfile.objects.get(user__username=username)
            if save_order:
                profile.default_phone_number = shipping_details.phone
                profile.default_country = shipping_details.address.country
                profile.default_county = shipping_details.address.state
                profile.default_town_r_city = shipping_details.address.city
                profile.default_street_add_line1 = (
                    shipping_details.address.line1)
                profile.default_street_add_line2 = (
                    shipping_details.address.line2)
                profile.default_postcode = shipping_details.address.postal_code
                profile.save()

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.full_name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    county__iexact=shipping_details.address.state,
                    town_r_city__iexact=shipping_details.address.city,
                    street_add_line1__iexact=shipping_details.address.line1,
                    street_add_line2__iexact=shipping_details.address.line2,
                    postcode__iexact=shipping_details.address.postal_code,
                    grand_total=grand_total,
                    original_basket=basket,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(content=f"Webhook recieved: {event['type']}"
                                        " S: Order already in db",
                                        status=200)
        else:
            order = None
            try:
                order = Order.objects.get(
                    full_name=shipping_details.name,
                    user_profile=profile,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    county=shipping_details.address.state,
                    town_r_city=shipping_details.address.city,
                    street_add_line1=shipping_details.address.line1,
                    street_add_line2=shipping_details.address.line2,
                    postcode=shipping_details.address.postal_code,
                    original_basket=basket,
                    stripe_pid=pid,
                )
                for i in range(0, len(json.loads(basket))-1):
                    item_id = basket[i]["pk"]
                    item_data = basket[i]["quantity"]
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_item = Order_Items(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_item.save()
            except Exception:
                if order:
                    order.delete()
                return HttpResponse(content=(
                    f"Webhook recieved: {event['type']}"),
                                    status=500)
        self._send_confirmation_email(order)
        return HttpResponse(content=f"Webhook recieved: {event['type']}",
                            status=200)

    def handle_failed_payment(self, event):
        return HttpResponse(content=f"Webhook recieved: {event['type']}",
                            status=200)
