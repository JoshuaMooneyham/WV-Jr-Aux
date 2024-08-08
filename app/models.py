from django.db import models

# Create your models here.
class UpcomingEvent(models.Model):
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

class Project(models.Model):
    title = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)