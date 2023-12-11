from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    user_id = models.IntegerField(unique=True,  blank=True, null=True)
    
    # Add unique related_name attributes for groups and user_permissions
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_user_permissions',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

