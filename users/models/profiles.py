"""Profile model"""

# Django
from django.db import models

# Utils
from utils.models import TweetmeBaseModel

# Models
from users.models import User

class Profile(TweetmeBaseModel):
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    picture = models.ImageField(
        'profile_picture',
        upload_to='users/pictures/',
        blank=True,
        null=True
    )

    biografia = models.TextField(max_length=500, blank=True, null=True)

    #followers = models.ManyToManyField(User, related_name='following')
