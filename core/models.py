from django.db import models
from django.contrib.auth.models import User

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

class Farmer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    village = models.CharField(max_length=100)
    contact = models.CharField(max_length=20)
    farm_type = models.CharField(max_length=50)
    acres = models.FloatField(default=1.0)
    crop = models.CharField(max_length=50)
    duration = models.IntegerField(default=120)
    seed_quantity = models.CharField(max_length=50)
    start_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.crop}"

class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    temperature = models.FloatField()
    rainfall = models.FloatField()
    ph = models.FloatField()
    plot = models.CharField(max_length=100, default='Main Field')
    results = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recommendation for {self.user.username if self.user else 'Guest'} on {self.timestamp}"
