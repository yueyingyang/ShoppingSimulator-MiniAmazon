from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.decorators import login_required

class Warehouse(models.Model):
    x = models.IntegerField(default=1)
    y = models.IntegerField(default=1)

class my_user(AbstractUser):
    email = models.EmailField(unique=True, max_length=255)
    username = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Package(models.Model):
    # Auto-generated package_id
    wh = models.ForeignKey(Warehouse, default=None, related_name="wh", on_delete=models.DO_NOTHING, blank=True, null=True)
    truck_id = models.IntegerField(default=None, blank=True, null=True)
    addr_x = models.IntegerField(default=1)
    addr_y = models.IntegerField(default=1)
    # Item list str Format: "id1:description1:count1;id2:description2:count2"
    # Use join and split
    # Reference: https://www.geeksforgeeks.org/python-program-to-convert-a-list-to-string/
    item_str = models.TextField(default="")

    CREATED = 0
    PURCHASING = 1
    PURCHASED = 2
    PACKING = 3
    PACKED = 4
    LOADING = 5
    LOADED = 6
    DELIVERING = 7
    DELIVERED = 8
    CANCEL = 9

    PKG_STATUS = [
        (CREATED, 'CREATED'),
        (PURCHASING, 'PURCHASING'),
        (PURCHASED, 'PURCHASED'),
        (PACKING, 'PACKING'),
        (PACKED, 'PACKED'),
        (LOADING, 'LOADING'),
        (LOADED, 'LOADED'),
        (DELIVERING, 'DELIVERING'),
        (DELIVERED, 'DELIVERED'),
        (CANCEL, 'CANCEL')
    ]
    status = models.IntegerField(default=CREATED, choices=PKG_STATUS)
    upsAccount = models.TextField(default=None, blank=True, null=True)
    user = models.ForeignKey(my_user, default=None, related_name="user", on_delete=models.DO_NOTHING)


# Front end catalog
class Product(models.Model):
    description = models.CharField(max_length=100)





