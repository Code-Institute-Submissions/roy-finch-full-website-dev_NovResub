import json

from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail

import stripe

from profiles.models import UserProfile
from profiles.forms import ProfileForm
from products.models import Product
from basket.contexts import basket_contents
from .forms import OrderForm
from .models import Order, Order_Items


@require_POST
def cache_checkout_data(request):
    """
    This function will cache any data about the checkout
    so that it can be accessed from other entries
    It also adds data to the stripe payment intent that
    is created to make sure that the payment is sufficent
    and worked.
    """
    try:
        pid = request.POST.get("client_secret").split("_secret")[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.retrieve(pid)
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, "Sorry your payment cant be"
                                " proccessed right now."
                                " Please try again later.")
        return HttpResponse(content=e, status=400)


def checkout(request):
    """
    This sets up the form for checking out
    and also sets up the stripe payment and view
    """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    basket = request.session.get("basket", [])

    if request.method == "POST":
        """ This checks for the post in request.method, and updates
        the information on the users profile and begins to
        sort out the payment and other responsive functions
        what are required to fire during this instance """
        form_data = {
            "full_name": request.POST["full_name"],
            "email": request.POST["email"],
            "phone_number": request.POST["phone_number"],
            "country": request.POST["country"],
            "county": request.POST["county"],
            "town_r_city": request.POST["town_r_city"],
            "street_add_line1": request.POST["street_add_line1"],
            "street_add_line2": request.POST["street_add_line2"],
            "postcode": request.POST["postcode"]
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = request.POST.get("client_secret").split("_secret")[0]
            order.stripe_pid = pid
            order.original_basket = json.dumps(basket)
            order.save()
            for i in range(0, len(basket)):
                try:
                    product = Product.objects.get(id=basket[i]["pk"])
                    if isinstance(basket[i]["quantity"], int):
                        indiv_items = Order_Items(
                            order=order,
                            product=product,
                            quantity=basket[i]["quantity"],
                            indiv_item_total=(
                                basket[i]["product"]["price"]*basket[i]["quantity"])
                        )
                        indiv_items.save()
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the items wasn't found,"
                        "please contact us for more information."))
                    order.delete()
                    return redirect(reverse("view_basket"))

            request.session["save_order"] = "save-order" in request.POST
            return redirect(reverse(
                "checkout_success", args=[order.order_number]))

        else:
            messages.error(request, ("Error, problem with form"))
    else:
        if not basket:
            messages.error(request, "Theres nothing in your basket the moment")
            return redirect(reverse("products"))
        current_basket = basket_contents(request)
        total = current_basket["grand_total"]
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    "full_name": profile.user.get_full_name(),
                    "email": profile.user.email,
                    "phone_number": profile.default_phone_number,
                    "country": profile.default_country,
                    "county": profile.default_county,
                    "town_r_city": profile.default_town_r_city,
                    "street_add_line1": profile.default_street_add_line1,
                    "street_add_line2": profile.default_street_add_line2,
                    "postcode": profile.default_postcode,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

    if not stripe_public_key or not stripe_secret_key:
        """ This is a check to make sure that you have set the stripe keys """
        messages.warning(request, "Stripe key is not set.")
    """ This gets an order form from the forms.py and
    then sets the template, and context and renders the
    information. """
    
    template = "checkout/checkout.html"
    context = {
        "order_form": order_form,
        "stripe_public_key": stripe_public_key,
        "client_secret": intent.client_secret,
        "can_display": False
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Function for when a payment is successful
    it will take the user to a page dedicated to
    the order number and info the user would need
    afterwards
    """
    save_order = request.session.get('save_order')
    order = get_object_or_404(Order, order_number=order_number)
    """ This checks if the user wants to save their order
    then gets their profile and adjusts it corrisponding
    the users input and then begin to render
    a success checkout page with information about the purchase. """
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()

    if save_order:
        profile_data = {
            "default_phone_number": order.phone_number,
            "default_country": order.country,
            "default_county": order.county,
            "default_street_add_line1": order.street_add_line1,
            "default_street_add_line2": order.street_add_line2,
            "default_town_r_city": order.town_r_city,
            "default_postcode": order.postcode
        }
        profile_form = ProfileForm(profile_data, instance=profile)
        if profile_form.is_valid():
            profile_form.save()

    if "basket" in request.session:
        del request.session["basket"]

    template = "checkout/checkout_success.html"
    context = {
        "order": order
    }

    return render(request, template, context)
