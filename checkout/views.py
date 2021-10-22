import json

from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings

import stripe

from products.models import Product
from basket.contexts import basket_contents
from .forms import OrderForm
from .models import Order, Order_Items


@require_POST
def cache_checkout_data(request):
    """
    This function will cache any data about the checkout
    so that it can be accessed from other entries
    """
    try:
        pid = request.POST.get("client_secret").split("_secret")[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            "basket": json.dumps(request.session["basket"]),
            "save_order": request.POST.get("save_order"),
            "username": request.user,
        })
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
        form_data = {
            "full_name": request.POST["full_name"],
            "email": request.POST["email"],
            "phone_number": request.POST["phone_number"],
            "country": request.POST["country"],
            "county": request.POST["county"],
            "town_r_city": request.POST["town_r_city"],
            "street_add_line1": request.POST["street_add_line1"],
            "street_add_line2": request.POST["street_add_line2"],
            "postcode": request.POST["postcode"],
        }
        order_form = OrderForm(form_data)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = request.POST.get("client_key").split("_secret")[0]
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
                    return redirect(reverse("view_bag"))

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
            currency=settings.STRIPE_CURRENCY
        )

    if not stripe_public_key or not stripe_secret_key:
        messages.warning(request, "Stripe key is not set.")

    order_form = OrderForm()
    template = "checkout/checkout.html"
    context = {
        "order_form": order_form,
        "stripe_public_key": stripe_public_key,
        "client_key": intent.client_secret,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Function for when a payment is successful
    it will take the user to a page dedicated to
    the order number and info the user would need
    afterwards
    """
    order = get_object_or_404(Order, order_number=order_number)

    if "basket" in request.session:
        del request.session["basket"]

    template = "checkout/checkout_success.html"
    context = {
        "order": order
    }

    return render(request, template, context)
