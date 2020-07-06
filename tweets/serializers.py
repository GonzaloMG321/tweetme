"""Tweets serializers"""

# Conf
from django.conf import settings

# Django Rest Framework
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

# Models
from .models import Tweet, TweetLike

# Serializers
from users.serializers import UserProfileSerializer

MAX_TWEET_LENGTH = settings.MAX_TWEET_LENGTH
TWEET_ACTION_OPTIONS = settings.TWEET_ACTION_OPTIONS

class TweetActionSerializer(serializers.Serializer):
    action = serializers.CharField()
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_action(self, value):
        value = value.lower().strip()
        if not value in TWEET_ACTION_OPTIONS:
            raise serializers.ValidationError('This is not a valid option')
        return value
    
    def validate(self, data):
        tweet = self.context['tweet']
        user = data['user']
        if data['action'] == 'like':
            if tweet.likes.filter(id=user.id).exists():
                raise serializers.ValidationError('Ya te gusta este tweet')

        if data['action'] == 'unlike':
            if not tweet.likes.filter(id=user.id).exists():
                raise serializers.ValidationError('Aun no te gusta este tweet')
        return data
    
    def create(self, data):
        user = data['user']
        tweet = self.context['tweet']
        if data['action'] == 'like':
            TweetLike.objects.create(user=user, tweet=tweet)
        if data['action'] == 'unlike':
            tweelike = TweetLike.objects.filter(user=user, tweet=tweet)
            tweelike.delete()
        return data

class TweetCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tweet
        fields = ['content']

    def validate_content(self, value):
        if len(value) > 250:
            raise serializers.ValidationError('This tweet is too long')
        return value

    def create(self, data):
        user = self.context['user']
        tweet = Tweet.objects.create(content=data['content'], user=user)
        return tweet

class TweetParentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    likes = serializers.SerializerMethodField(read_only=True)
    user_like_it = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tweet
        fields = ['id', 'content', 'likes', 'user_like_it', 'user']
    
    def get_likes(self, obj):
        return obj.likes.count()

    def get_user_like_it(self, obj):
        user = self.context['user']
        if not user.is_anonymous:
            return obj.likes.filter(id=user.id).exists()
        return False

class BasicTweetSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField(read_only=True)
    parent = TweetParentSerializer(read_only=True)
    user_like_it = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tweet
        fields = ['id', 'content', 'likes', 'is_retweet', 'parent', 'user_like_it']
    
    def get_likes(self, obj):
        return obj.likes.count()
    
    def get_user_like_it(self, obj):
        user = self.context['user']
        if not user.is_anonymous:
            return obj.likes.filter(id=user.id).exists()
        return False

class TweetSerializer(BasicTweetSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta(BasicTweetSerializer.Meta):
        fields = BasicTweetSerializer.Meta.fields + ['user']
    


class RetweetSerializers(serializers.Serializer):
    content = serializers.CharField(allow_blank=True, required=False)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_content(self, value):
        if len(value) > 250:
            raise serializers.ValidationError('This tweet is too long')
        return value
    
    def create(self, data):
        tweet = self.context['tweet']
        user = data['user']

        newTweet = Tweet.objects.create(user=user, content=data['content'], parent=tweet)
        return newTweet

