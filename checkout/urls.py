from django.urls import path
from . import views
from .webhooks import webhook
""" These are the url configs for the checkout,
there are several url paths for the checkout, and
checkout success
along with the webhooks wh url and the
cache of data on purchase at the
cache_checkout_data url. """
urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('checkout_success/<order_number>',
         views.checkout_success, name='checkout_success'),
    path('cache_checkout_data/',
         views.cache_checkout_data, name='cache_checkout_data'),
    path('wh/', webhook, name='webhook'),
]
