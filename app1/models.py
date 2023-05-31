from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class MyUser(AbstractUser):
    mobile_number = models.CharField(max_length=10)
    avatar = models.ForeignKey('Avatar', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'User'


class Avatar(models.Model):
    child_name = models.CharField(max_length=100)
    avatar_image = models.CharField(max_length=200)
    class Meta:
        db_table = 'Avtar'


class MyModel(models.Model):
    OPTION_CHOICES = (
        ('Assamese', 'Assamese'),
        ('Bengali', 'Bengali'),
        ('English', 'English'),
        ('Gujarati', 'Gujarati'),
        ('Hindi', 'Hindi'),
        ('Kannada', 'Kannada'),
        ('Malayalam', 'Malayalam'),
        ('Marathi', 'Marathi'),
        ('Odiya', 'Odiya'),
        ('Punjabi', 'Punjabi'),
        ('Tamil', 'Tamil'),
        ('Telugu', 'Telugu'),
        ('Urdu', 'Urdu'),
    )
    option = models.CharField(max_length=10, choices=OPTION_CHOICES)

class Aop_lan(models.Model):
    OPTION_CHOICES = (
       
        ('English', 'English'),

    )
    option = models.CharField(max_length=10, choices=OPTION_CHOICES)

class Aop_sub_lan(models.Model):
    OPTION_CHOICES = (
       
        ('BL', 'BL'),
        ('ML1', 'ML1'),
        ('ML2', 'ML2'),
        ('EL', 'EL'),

    )
    option = models.CharField(max_length=10, choices=OPTION_CHOICES)

class Program(models.Model):
    OPTION_CHOICES = (
        ('General Program', 'General Program'),
        ('AOP Program', 'AOP Program'),
        ('Advance English Program', 'Advance English Program'),
     
    )
    option = models.CharField(max_length=50, choices=OPTION_CHOICES)
