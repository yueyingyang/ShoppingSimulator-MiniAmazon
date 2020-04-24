from django.contrib import admin
from .models import Package, Product, Warehouse, my_user

admin.site.register(Package)
admin.site.register(Product)
admin.site.register(Warehouse)
admin.site.register(my_user)
# Register your models here.
