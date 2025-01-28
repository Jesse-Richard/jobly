from django.db import models
import datetime
# Create your models here.
class Logger(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(help_text='Please enter your email address')
    skills = models.CharField(max_length=500, help_text='Please enter your skills')
    workexp = models.CharField(max_length=2000, help_text='Please enter your work experience')
    created_at = models.DateTimeField(default=datetime.datetime.now())