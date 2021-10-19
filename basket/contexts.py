from django.conf import settings


def basket_contents(request):
    """
    Deals with the basket and alters the
    corrisponding values for other apps.
    """

    total = 0
    product_count = 0
    shipping_total = 0
    basket = request.session.get("basket", {})

    for x in range(0, len(basket)):
        total += basket[x]["product"]["price"] * int(basket[x]["quantity"])
        product_count += basket[x]["quantity"]
        shipping = round((
            basket[x]["quantity"]*basket[x]["product"]["price"])*(
            settings.STANDARD_DELIVERY_PERCENTAGE/100), 2)
        shipping_total += shipping
        basket[x] = {
                "pk": basket[x]["pk"],
                "quantity": basket[x]["quantity"],
                "product": basket[x]["product"],
                "shipping": shipping,
                "total_cost": basket[x]["quantity"]*(
                    shipping+basket[x]["product"]["price"]),
            }

    grand_total = total+round(
        total * settings.STANDARD_DELIVERY_PERCENTAGE/100, 2)
    context = {
        "basket_contents": basket,
        "total": total,
        "shipping_total": shipping_total,
        "grand_total": grand_total,
        "product_count": product_count,
    }

    return context
