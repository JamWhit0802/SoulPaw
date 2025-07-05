from django.db import models

class TodoItem(models.Model):
    """
    Model representing a to-do item.
    """
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
# Create your models here.
