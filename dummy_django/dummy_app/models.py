from django.db import models

# Create your models here.


class DummyModel(models.Model):
    name = models.CharField(max_length=255)
    name2 = models.CharField(max_length=255, default='fuck')
