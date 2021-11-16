from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Order_Items
""" This is to recieve the signals to update the total. """


@receiver(post_save, sender=Order_Items)
def update_save(sender, instance, created, **kwargs):
    instance.order.update_total()


@receiver(post_delete, sender=Order_Items)
def update_delete(sender, instance, **kwargs):
    instance.order.update_total()
