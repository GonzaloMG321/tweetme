# Django
from django.shortcuts import render
from django.http import JsonResponse

# Django Rest Framework
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, mixins, status

# Filters
from django_filters.rest_framework import DjangoFilterBackend
from tweets.filters import TweetFilter

# Serializers
from .serializers import (
    TweetSerializer,
    TweetActionSerializer,
    TweetCreateSerializer,
    RetweetSerializers,
    BasicTweetSerializer,
    CommentCreateSerializer,
    CommentSerializer
    )

# Models
from tweets.models import Tweet, Comment

# Permissions
from rest_framework.permissions import IsAuthenticated
from tweets.permissions import IsOwnerTweet



class TweetViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet):
    """Tweet viewset """
    queryset = Tweet.objects.all()

    filter_backends = [DjangoFilterBackend]
    filterset_class = TweetFilter


    def get_permissions(self):
        permissions = []
        if self.action in ['retweet','like', 'create', 'destroy', 'update', 'partial_update', 'feed', 'comment']:
            permissions.append(IsAuthenticated)
        if self.action in ['destroy', 'update', 'partial_update']:
            permissions.append(IsOwnerTweet)
        return [permission() for permission in permissions]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TweetCreateSerializer
        if self.action == 'like':
            return TweetActionSerializer
        if self.action == 'retweet':
            return RetweetSerializers
        if self.action == 'comment':
            return CommentCreateSerializer
        return TweetSerializer

    def get_serializer_context(self):
        context = super(TweetViewSet, self).get_serializer_context()
        context['user'] = self.request.user
        return context

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        serializer = serializer_class(
            data=request.data, 
            context=context
        )
        serializer.is_valid(raise_exception=True)
        tweet = serializer.save()

        read_serializer = TweetSerializer(tweet, context=context)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)


    @action(detail=True, methods=['post'])
    def like(self, request, *args, **kwargs):
        tweet = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            data=request.data,
            context={
                'request': request,
                'tweet': tweet
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post'])
    def retweet(self, request, *args, **kwargs):
        tweet = self.get_object()
        context = self.get_serializer_context()
        context['tweet'] = tweet
        context['request'] = request
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        newTweet = serializer.save()
        serializer_new = TweetSerializer(newTweet, context=context)
        return Response(serializer_new.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def feed(self, request, *args, **kwargs):
        user = request.user
        qs = Tweet.objects.all().feed(user)
        page = self.paginate_queryset(qs)

        context = self.get_serializer_context()
        serializer = TweetSerializer(
            page,
            many=True,
            context=context
        )

        result = self.get_paginated_response(serializer.data)
        
        return Response(result.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def comment(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        tweet = self.get_object()

        context['tweet'] = tweet

        serializer = serializer_class(
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @comment.mapping.get
    def get_comments(self, request, pk=None):
        tweet = self.get_object()
        context = self.get_serializer_context()
        qs = Comment.objects.filter(tweet=tweet)

        page = self.paginate_queryset(qs)
        serializer = CommentSerializer(
            page,
            many=True,
            context=context
        )
        result = self.get_paginated_response(serializer.data)
        return Response(result.data, status=status.HTTP_200_OK)