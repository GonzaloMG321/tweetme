from django.db import models
from django.conf import settings
from django.db.models import Q

# Utils
from utils.models import TweetmeBaseModel

User = settings.AUTH_USER_MODEL

class TweetQuerySet(models.QuerySet):
    def feed(self, user):
        users_exist = user.followings.exists()
        followed_user_id = []
        if users_exist:
            followed_user_id = user.followings.values_list("id", flat=True)
        return self.filter(
            Q(user__id__in=followed_user_id) | Q(user=user)
        ).select_related('user').distinct().order_by('-created')


class TweetManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return TweetQuerySet(self.model, using=self._db)
    

class TweetLike(TweetmeBaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tweet = models.ForeignKey('Tweet', on_delete=models.CASCADE)


class Tweet(TweetmeBaseModel):
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tweets')
    content =  models.TextField(blank=True, null=True)
    image = models.FileField(upload_to='images/', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='tweet_user', through=TweetLike, blank=True)
    
    objects = TweetManager()

    class  Meta: 
        ordering = ['-created']

    @property
    def is_retweet(self):
        return self.parent != None

    def __str__(self):
        return self.content

class Comment(TweetmeBaseModel):
    user = models.ForeignKey(User, related_name='comentarios', on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet, related_name='comentario', on_delete=models.CASCADE)
    content = models.TextField()

    class  Meta: 
        ordering = ['-created']
