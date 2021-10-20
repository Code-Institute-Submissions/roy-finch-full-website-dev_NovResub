from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product
from django.forms.models import model_to_dict


def view_basket(request):
    """ This function is to control the basic
    rendering of the basket when on the basket/ url
    this can deal with post requests to add
    or remove items from the basket, by detecting
    which request the user wants, and calling
    the update_basket function to inact those
    effects the user would like to do to the
    basket """

    if "add" in request.POST:
        update_basket(request, True, request.POST["add"])
        return redirect("/basket/")
    elif "remove" in request.POST:
        update_basket(
                request, False, request.POST["remove"])
        return redirect("/basket/")

    return render(request, "basket/basket.html")


def update_basket(request, add, product_pk):
    """ This is a function to control the items
    within the basket, this function is used on
    other views pages to reuse this function """

    basket = request.session.get("basket", [])
    product = get_object_or_404(Product, pk=product_pk)

    if add:
        messages.success(request, f'Added { product.name }')
        if find_product(basket, product_pk) is not False:
            basket[find_product(basket, product_pk)]["quantity"] += 1
        else:
            basket.append({
                "pk": product_pk,
                "product": model_to_dict(product, exclude=["price", "rating", "image"]),
                "quantity": 1,
            })
            basket[len(basket)-1]["product"]["price"] = float(product.price)
            basket[len(basket)-1]["product"]["rating"] = float(product.rating)
            basket[len(basket)-1]["product"]["image"] = str(product.image)
    else:
        messages.success(request, f'Removed { product.name }')
        if find_product(basket, product_pk) is not False and basket[
                find_product(basket, product_pk)]["quantity"] > 1:
            basket[find_product(basket, product_pk)]["quantity"] -= 1
        elif find_product(basket, product_pk) is not False and basket[
                find_product(basket, product_pk)]["quantity"] == 1:
            del basket[find_product(basket, product_pk)]

    request.session["basket"] = basket

    return basket


def find_product(dic, pk):
    """ Quick function to find products within the basket
    as I have altered the way on which the basket
    is accessed the basket is actual a list, dictionary
    combi, whilst it would be better to use a dictionary
    I used this combi to help with production as this works
    equally as well as it would if the basket was just a
    dictionary """

    for i in range(0, len(dic)):
        if dic[i]["pk"] == pk:
            return i
    return False
