from django.urls import path
from . import views
""" These are the url configs for products,
Pathways for the customers like view products, or 
view product which show one or all of the products
on a rendered page, the others are for admin
users to edit products """
urlpatterns = [
    path('', views.all_products, name='products'),
    path('<int:product_pk>/', views.product_detail, name='product_detail'),
    path('add/', views.add_product, name='add_product'),
    path('find/', views.find_product, name='find_product'),
    path('edit/<int:product_pk>/', views.edit_product, name='edit_product'),
]
