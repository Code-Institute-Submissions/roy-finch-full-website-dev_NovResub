import uuid

from django.db import models
from django.db.models import Sum
from products.models import Product
from django.conf import settings

from django_countries.fields import CountryField
from profiles.models import UserProfile


class Order(models.Model):
    """
    These are the order models, which
    is used to make sure that an order
    has the specific information that
    is required.
    """
    order_number = models.CharField(max_length=32, null=False, editable=False)
    user_profile = models.ForeignKey(UserProfile, null=True, blank=True,
                                     on_delete=models.CASCADE,
                                     related_name="orders")
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = CountryField(blank_label="Country",
                           null=False, blank=False)
    postcode = models.CharField(max_length=20, null=False, blank=False)
    town_r_city = models.CharField(max_length=20, null=False, blank=False)
    street_add_line1 = models.CharField(max_length=80, null=False, blank=False)
    street_add_line2 = models.CharField(max_length=80, null=False, blank=False)
    county = models.CharField(max_length=80, null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(
        max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, default=0)
    stripe_pid = models.CharField(max_length=254, null=False, blank=False,
                                  default="")

    def _gen_order_number(self):
        return uuid.uuid4().hex.upper()

    def update_total(self):
        self.order_total = self.indiv_items.aggregate(
            Sum("indiv_item_total"))["indiv_item_total__sum"] or 0
        self.delivery_cost = (
            self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._gen_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class Order_Items(models.Model):
    """
    This is to call upon a specific item which
    is in the parent Model class Order.
    """
    order = models.ForeignKey(
        Order, null=False, blank=(
            False), on_delete=models.CASCADE, related_name="indiv_items")
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    indiv_item_total = models.DecimalField(
        max_digits=(
            6), decimal_places=2, null=False, blank=False, editable=False)

    def __str__(self):
        return f'PK {self.product.pk} on order {self.order.order_number}'

    def save(self, *args, **kwargs):
        self.indiv_item_total = self.product.price * self.quantity
        super().save(*args, **kwargs)
