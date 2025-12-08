"""
Admin configuration for the dealership application

Register django models with the admin site to enable management of car makes
and car models through the django admin interface.
"""

from django.contrib import admin
from .models import CarMake, CarModel

# Register your models here

admin.site.register(CarMake)
admin.site.register(CarModel)
