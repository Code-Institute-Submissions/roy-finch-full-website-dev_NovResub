from django.urls import path
from . import views
""" This is the urls config for the index. """
urlpatterns = [
    path('', views.index, name='home'),
]