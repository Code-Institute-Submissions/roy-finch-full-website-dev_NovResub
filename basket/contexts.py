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
        total += basket[str(x)]["product"]["price"] * int(basket[str(x)]["quantity"])
        product_count += basket[str(x)]["quantity"]
        shipping = round((
            basket[str(x)]["quantity"]*basket[str(x)]["product"]["price"])*(
            settings.STANDARD_DELIVERY_PERCENTAGE/100), 2)
        shipping_total += shipping
        basket[str(x)] = {
                "pk": basket[str(x)]["pk"],
                "quantity": basket[str(x)]["quantity"],
                "product": basket[str(x)]["product"],
                "shipping": shipping,
                "total_cost": basket[str(x)]["quantity"]*(
                    shipping+basket[str(x)]["product"]["price"]),
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