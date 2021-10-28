from django.shortcuts import render


def index(request):
    """ A view for the index page, """
    context = {
        "can_display": True
    }
    return render(request, "home/index.html", context)
