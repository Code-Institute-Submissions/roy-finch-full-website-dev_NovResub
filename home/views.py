from django.shortcuts import render


def index(request):
    """ A view for the index page, """
    request.session["basket"] = {}
    return render(request, "home/index.html")
