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

    seguidores = models.ManyToManyField(
        'users.User',
        through='users.Seguidor',
        through_fields=('siguiendo', 'seguidor')
    )


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['nombre', 'apellido_paterno', 'email']


    objects = MyUserManager()
    
    def __str__(self):
        """Return username"""
        return self.username


class Seguidor(TweetmeBaseModel):
    seguidor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='seguidor'
    )

    siguiendo = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='siguiendo'
    )

    def __str__():
        return '{} está siguiendo a {}'.format(seguidor.username, siguiendo.username)
