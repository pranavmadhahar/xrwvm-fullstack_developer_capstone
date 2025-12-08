"""
Django models for the dealership application.

Defines database schema for car makes and car models
Each class represents a table in the database and includes fields
for storing relevant attributes.
"""

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here
class CarMake(models.Model):
    """
    Represents car entity in dealership system.
    Stores car's make or brand.
    """

    name = models.CharField(max_length=50, blank=False, null=False)
    description = models.CharField(max_length=300, blank=False, null=False)

    def __str__(self):
        return str(self.name)


class CarModel(models.Model):
    """
    Represents car entity in dealership system.
    Stores car's model or brand's model
    """

    # create list containing tuples of car types
    BODY_TYPES = [
        ("SEDAN", "sedan"),
        ("SUV", "suv"),
        ("HATCHBACK", "hatchback"),
        ("WAGON", "wagon"),
    ]
    # Assign CarMake as foreignkey
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=BODY_TYPES, default="SEDAN")
    # Use django's min & max validators
    year = models.IntegerField(
        validators=[MinValueValidator(2015), MaxValueValidator(2023)]
    )

    def __str__(self):
        return str(self.name)
