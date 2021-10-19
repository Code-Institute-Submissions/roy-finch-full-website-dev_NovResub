from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from django.db.models import Q
from django.db.models.functions import Lower
from basket.views import update_basket

consoles = ["No Specific Console", "Nintendo 64", "NES", "SNES"]
categories = ["All", "Consoles", "Games", "Accessories", "Bundles"]


def all_products(request):
    """ This is the view for the products """
    products = Product.objects.all()

    search = None
    search_num = None
    ids = [0, 0]
    sortkey = None
    query = ["", "", ""]

    basket = request.session.get("basket", [])
    print(basket)

    if request.GET:
        if "search" not in request.GET and (
                "c" in request.GET) and (
                    "q" in request.GET) and (
                        "f" in request.GET):
            query = [request.GET["c"], request.GET["q"], request.GET["f"]]
            if query[2] != "":
                if query[2] == "A-Z":
                    sortkey = f'{"lower_name"}'
                    products = products.annotate(lower_name=Lower("name"))
                if query[2] == "Z-A":
                    sortkey = f'-{"lower_name"}'
                    products = products.annotate(lower_name=Lower("name"))
                if query[2] == "Ascending Price":
                    sortkey = f'{"price"}'
                if query[2] == "Decending Price":
                    sortkey = f'-{"price"}'
                if query[2] == "Rating":
                    sortkey = f'{"rating"}'
                if sortkey is not None:
                    products = products.order_by(sortkey)
            if not query:
                return redirect("home")
            if query[0] in consoles:
                ids[0] = consoles.index(query[0])
            else:
                ids[0] = 0
                query[0] = "No Specific Console"
            if query[1] in categories:
                ids[1] = categories.index(query[1])
            else:
                ids[1] = 0
                query[1] = "All"
            if query[0] == "No Specific Console" and query[1] != "All":
                queries = Q(category=ids[1])
            elif query[1] == "All" and query[0] != "No Specific Console":
                queries = Q(console=ids[0])
            else:
                queries = Q(console=ids[0]) & Q(category=ids[1])

            if (query[0] != "No Specific Console" or query[1] != "All"):
                products = products.filter(queries)
            else:
                products = Product.objects.all()
        else:
            search = request.GET["search"]
            queries = Q(
                name__icontains=search) | Q(description__icontains=search)
            products = products.filter(queries)

    search_num = len(products)

    context = {
        "products": products,
        "search_q": search,
        "return_num": search_num,
        "basket_contents": basket,
        "can_display": True
    }

    if request.POST:
        if "add" in request.POST:
            check_request(request, request.POST["add"])
            return redirect("/products/#id"+request.POST["add"])

    return render(request, "products/products.html", context)


def check_request(request, product_pk):
    """
    Checks whether a request is to add
    or remove an item from the basket
    this is done as the basket is a list, dict
    and needs to be accessed using the function inside
    the views.py basket/
    """
    if request.POST:
        if "add" in request.POST:
            update_basket(request, True, product_pk)
        elif "remove" in request.POST:
            update_basket(request, False, product_pk)


def product_detail(request, product_pk):
    """ This will display the page of the item that has been selected."""

    products = get_object_or_404(Product, pk=product_pk)

    basket = request.session.get("basket", [])

    if request.POST:
        check_request(request, product_pk)

    context = {
        "products": products,
        "basket_contents": basket,
        "can_display": True
    }

    return render(request, "products/product.html", context)
