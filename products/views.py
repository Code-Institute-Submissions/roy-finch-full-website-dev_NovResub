from django.shortcuts import render


def all_products(request):
    """ This is the view for the products """

    return render(request, "products/products.html")
