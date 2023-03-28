from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class MyUser(AbstractUser):
    mobile_number = models.CharField(max_length=10, unique=True)
    avatar = models.ForeignKey('Avatar', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'User'


class Avatar(models.Model):
    child_name = models.CharField(max_length=100)
    avatar_image = models.CharField(max_length=200)
    class Meta:
        db_table = 'Avtar'


