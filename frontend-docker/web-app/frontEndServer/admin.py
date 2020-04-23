from django.contrib import admin
from .models import Package, Product, Warehouse

admin.site.register(Package)
admin.site.register(Product)
admin.site.register(Warehouse)

# Register your models here.
