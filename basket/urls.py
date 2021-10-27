from django.urls import path
from . import views
""" This the urls config for the basket, there is just the
basket view which leads
to the checkout once you press checkout and you get to the basket
by clicking the basket
in the bottom left at any point. """
urlpatterns = [
    path('', views.view_basket, name='basket'),
]
