from django.shortcuts import render
from .forms import OrderForm


def checkout(request):
    """
    This sets up the form for checking out
    and also sets up the stripe payment and view
    """
    order_form = OrderForm()

    context = {
        "order_form": order_form,
    }

    return render(request, "checkout/checkout.html", context)
