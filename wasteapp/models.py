from django.db import models

# Create your models here.

class Waste(models.Model):

    WASTE_TYPES = [
        ('Plastic','Plastic'),
        ('Paper','Paper'),
        ('Metal','Metal'),
        ('Organic','Organic'),
    ]

    STATUS = [
        ('Generated','Generated'),
        ('Collected','Collected'),
        ('Recycled','Recycled'),
        ('Reused','Reused'),
    ]

    waste_type = models.CharField(max_length=20, choices=WASTE_TYPES)
    quantity = models.FloatField()
    source = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.waste_type