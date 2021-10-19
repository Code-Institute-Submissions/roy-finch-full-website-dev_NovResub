from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from django.forms.models import model_to_dict


def view_basket(request):

    if "add" in request.POST:
        update_basket(request, True, request.POST["add"])
        return redirect("/basket/")
    elif "remove" in request.POST:
        update_basket(
                request, False, request.POST["remove"])
        return redirect("/basket/")

    return render(request, "basket/basket.html")


def update_basket(request, add, product_pk):
    basket = request.session.get("basket", {})
    product = get_object_or_404(Product, pk=product_pk)

    if add:
        if find_product(basket, product_pk) is not False:
            basket[find_product(basket, product_pk)]["quantity"] += 1
        else:
            basket[len(basket)] = {
                "pk": product_pk,
                "product": model_to_dict(product, exclude=["price", "rating", "image"]),
                "price": float(product.price),
                "rating": float(product.rating),
                "image": str(product.image),
                "quantity": 1,
            }
    else:
        if find_product(basket, product_pk) is not False and basket[
                find_product(basket, product_pk)]["quantity"] > 1:
            basket[find_product(basket, product_pk)]["quantity"] -= 1
        elif find_product(basket, product_pk) is not False and basket[
                find_product(basket, product_pk)]["quantity"] == 1:
            del basket[find_product(basket, product_pk)]

    request.session["basket"] = basket

    return basket


def find_product(dic, pk):
    """
    Quick function to find products within the basket
    as I have altered the way on which the basket
    is accessed the basket is actual a list, dictionary
    combi, whilst it would be better to use a dictionary
    I used this combi to help with production as this works
    equally as well as it would if the basket was just a
    dictionary
    """

    for i in range(0, len(dic)):
        if dic[i]["pk"] == pk:
            return i
    return False
