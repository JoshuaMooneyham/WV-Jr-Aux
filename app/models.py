from django.db import models

# Create your models here.
class UpcomingEvent(models.Model):
    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)
    title = models.TextField()
    location = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f'Event: {self.title}'

class Project(models.Model):
    title = models.TextField()
    description = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f'Project: {self.title}'