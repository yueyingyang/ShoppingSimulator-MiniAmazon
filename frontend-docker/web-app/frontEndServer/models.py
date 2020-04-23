from django.db import models

class Warehouse(models.Model):
    x = models.IntegerField(default=1)
    y = models.IntegerField(default=1)

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


# Front end catalog
class Product(models.Model):
    description = models.CharField(max_length=100)

# Create your models here.
