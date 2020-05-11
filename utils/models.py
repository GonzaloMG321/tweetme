"""Djago models utils"""

# Django
from django.db import models

class TweetmeBaseModel(models.Model):
    """Tweetme model is the base model"""

    created = models.DateTimeField(
        'created_at',
        auto_now_add=True,
        help_text='Date time on which the objec was created'
    )

    modified = models.DateTimeField(auto_now=True)


    class Meta:
        """Meta option"""
        abstract = True
        get_latest_by = 'created',
        ordering = ['-created', '-modified']
