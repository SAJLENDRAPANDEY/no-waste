from django.db import models
from users.models import User
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Waste Model (Producer waste add karega)
class Waste(models.Model):

    producer = models.ForeignKey(User, on_delete=models.CASCADE)

    company = models.CharField(max_length=200,default="Unknown Company")

    waste_type = models.CharField(max_length=100)

    quantity = models.IntegerField()

    date = models.DateField(default=timezone.now)

    status = models.CharField(
        max_length=20,
        choices=[
            ('produced','Produced'),
            ('listed','Listed'),
            ('consumed','Consumed'),
            ('recycled','Recycled')
        ],
        default='produced'
    )

    description = models.TextField(blank=True)

    location = models.CharField(max_length=200)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company + " - " + self.waste_type


# Consumer Waste Request Model
class WasteRequest(models.Model):

    consumer = models.ForeignKey(User, on_delete=models.CASCADE)

    waste = models.ForeignKey(Waste, on_delete=models.CASCADE)

    quantity = models.IntegerField()

    message = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending','Pending'),
            ('approved','Approved'),
            ('rejected','Rejected')
        ],
        default='pending'
    )

    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.consumer.username + " request"
    
