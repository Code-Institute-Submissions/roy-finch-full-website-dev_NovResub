from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from django.db.models import Q
from django.db.models.functions import Lower

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
        "can_display": True
    }

    return render(request, "products/products.html", context)


def product_detail(request, product_pk):
    products = get_object_or_404(Product, pk=product_pk)

    context = {
        "products": products
    }

    return render(request, "products/product.html", context)
