from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with role support"""
    
    ROLE_CHOICES = [
        ('CUSTOMER', 'Customer'),
        ('TECHNICIAN', 'Technician'),
        ('ADMIN', 'Admin'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CUSTOMER'
    )
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    def is_customer(self):
        return self.role == 'CUSTOMER'
    
    def is_technician(self):
        return self.role == 'TECHNICIAN'
    
    def is_admin(self):
        return self.role == 'ADMIN'
