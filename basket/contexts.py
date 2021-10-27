from django.conf import settings


def basket_contents(request):
    """ Deals with the basket and alters the
    corrisponding values for other apps.
    Set the variables that are required for the basket screen, this includes the value
    of the basket with shipping and without, the product count and the basket contents
    that are on the get """
    total = 0
    product_count = 0
    shipping_total = 0
    basket = request.session.get("basket", {})

    for x in range(0, len(basket)):
        """ A for loop to look throuhg the basket and check its contents and
        apply a total value, shipping and grand total which are not created or
        updated when an item is added to the basket. This is done to keep track
        of the values required on the html."""
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
    """ The grand total is done at the end, as it just uses the total
    of all the products * the shipping percentage. 
    Also the context is the basket, and the altered values for the views.
    Return the basket context once updated."""
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
