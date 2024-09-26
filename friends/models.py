from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.contrib.postgres.indexes import GinIndex
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    """
    Defines User model with Role-based access control
    """
    ROLE_CHOICES = (
        ('read', 'Read'),
        ('write', 'Write'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='read')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # For admin site access
    date_joined = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'friends_users'
        indexes = [
            GinIndex(
                name='user_search_gin',
                fields=['first_name', 'last_name'],
                opclasses=['gin_trgm_ops', 'gin_trgm_ops'],
            ),
        ]

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email & Password are required by default

    def __str__(self):
        return self.email

class Friends_Request(models.Model):
    """
    Model for storing all pending/accept/reject Friends request with appropriate User Ids
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'friends_request'
        verbose_name_plural = 'Friends_Request'
        unique_together = ('sender', 'receiver')
        indexes = [
            models.Index(fields=['receiver', 'status']),
            models.Index(fields=['sender', 'status']),
        ]
    
    def __str__(self):
        return f"{self.sender} -> {self.receiver} ({self.status})"

class Friendships(models.Model):
    """
    Model for storing all the Accepted Friends details
    """
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='friendships_user1', on_delete=models.CASCADE
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='friendships_user2', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Friendships'
        unique_together = ('user1', 'user2')
        indexes = [
            models.Index(fields=['user1', 'user2']),
        ]
    
    def __str__(self):
        return f"Friendship between {self.user1} and {self.user2}"

class User_Activity(models.Model):
    """
    Model for storing all the User Activities
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='activities', on_delete=models.CASCADE
    )
    activity_type = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'friends_users_activity'
        verbose_name_plural = 'Users_Activities'

    def __str__(self):
        return f"{self.user.email} - {self.activity_type}"

class Blocks(models.Model):
    """
    Model for storing all Block Users Details
    """
    blocker = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='blocking', on_delete=models.CASCADE
    )
    blocked = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='blocked_by', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Blocks'
        unique_together = ('blocker', 'blocked')
        indexes = [
            models.Index(fields=['blocker', 'blocked']),
        ]
    
    def __str__(self):
        return f"{self.blocker} blocked {self.blocked}"


