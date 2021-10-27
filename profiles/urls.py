from django.urls import path
from . import views
""" Url configs for the profile, just profile url, as the
other features are handled using all-auth """
urlpatterns = [
    path('', views.profile, name='profile'),
]
