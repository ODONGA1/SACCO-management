from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    
    ROLE_CHOICES = (
        ('MEMBER', 'Member'),
        ('STAFF', 'Staff'),
        ('ADMIN', 'Admin'),
        ('SUPER_ADMIN', 'Super Admin'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MEMBER')
    username = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    def __str__(self):
        return self.username
    