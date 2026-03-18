from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


# ── WASTE MODEL ──────────────────────────────────────────
class Waste(models.Model):

    producer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    company      = models.CharField(max_length=200, default="Unknown Company")
    waste_type   = models.CharField(max_length=100)
    quantity     = models.IntegerField()
    date         = models.DateField(default=timezone.now)
    location     = models.CharField(max_length=100)

    status = models.CharField(
        max_length=20,
        choices=[
            ('produced',  'Produced'),

            ('listed',    'Listed'),
            ('consumed',  'Consumed'),
            ('recycled',  'Recycled'),
        ],
        default='produced'
    )

    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company} - {self.waste_type}"


# ── WASTE REQUEST ─────────────────────────────────────────
class WasteRequest(models.Model):

    consumer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    waste    = models.ForeignKey(Waste, on_delete=models.CASCADE)

    quantity = models.IntegerField()
    message  = models.TextField()

    email = models.EmailField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending',  'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )

    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.consumer.username} -> request"


# ── REQUIREMENT ───────────────────────────────────────────
class Requirement(models.Model):

    company    = models.CharField(max_length=200)
    waste_type = models.CharField(max_length=100)
    quantity   = models.IntegerField()
    location   = models.CharField(max_length=200)
    date       = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.company


# ── PROFILE ───────────────────────────────────────────────
class Profile(models.Model):

    ROLE_CHOICES = [
        ('producer', 'Producer'),
        ('consumer', 'Consumer'),
    ]

    user  = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    role  = models.CharField(max_length=20, choices=ROLE_CHOICES, default='consumer')
    phone = models.CharField(max_length=20, blank=True, default='')
    bio   = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    def is_producer(self):
        return self.role == 'producer'

    def is_consumer(self):
        return self.role == 'consumer'


# ── AUTO-CREATE PROFILE WHEN USER IS CREATED ─────────────
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()