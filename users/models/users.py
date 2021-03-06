"""User model"""

# Django
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)


# Utils
from utils.models import TweetmeBaseModel


class MyUserManager(BaseUserManager):
    def create_user(self, username, email, nombre, apellido_paterno, password=None):
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            nombre=nombre,
            apellido_paterno=apellido_paterno
        )

        user.set_password(password)
        user.save(using=self._db)
        #Profile.objects.create(user)
        return user

    def create_superuser(self, username, email, nombre, apellido_paterno, password):
        """Create a new user profile"""
        user = self.create_user(username, email, nombre, apellido_paterno, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(TweetmeBaseModel, AbstractBaseUser):
    username = models.CharField(unique=True, max_length=30)
    email = models.EmailField(
        'email del usuario',
        unique = True,
        error_messages = {
            'unique': 'Ya existe un usuario con este email'
        }
    )

    nombre = models.CharField(max_length=30)
    apellido_paterno = models.CharField(max_length=30)
    apellido_materno = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nombre', 'apellido_paterno', 'email']

    followers = models.ManyToManyField(
        'User',
        related_name='followings',
        through='FollowRelation',
        through_fields=('following', 'follower')
    )

    objects = MyUserManager()
    
    def __str__(self):
        """Return username"""
        return self.username


class FollowRelation(TweetmeBaseModel):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE);
    following = models.ForeignKey(User, on_delete=models.CASCADE);