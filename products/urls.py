from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    path('<int:product_pk>/', views.product_detail, name='product_detail'),
    path('add/', views.add_product, name='add_product'),
    path('find/', views.find_product, name='find_product'),
    path('edit/<int:product_pk>/', views.edit_product, name='edit_product'),
]
