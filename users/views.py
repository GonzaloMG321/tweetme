"""Users views"""

# Django
from django.shortcuts import render

# Django REST Framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, mixins, viewsets
from rest_framework.decorators import action
# Jwt
from rest_framework_simplejwt.views import TokenObtainPairView

# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions.users import IsProfileOwner

# Serializers
from .serializers import (
    MyTokenObtainPairSerializer, 
    CustomUserSerializer,
    UserSignUpSerializer,
    UserModelSerializer,
    UserProfileModelSerializer,
    FollowUnfollowUserSerializer
    )
from tweets.serializers import BasicTweetSerializer

# Models
from users.models import User, Seguidor
from tweets.models import Tweet

class ObtainTokenPairWithColorView(TokenObtainPairView):
    permission_classes = (AllowAny, )
    serializer_class = MyTokenObtainPairSerializer

class CustomUserCreate(APIView):
    permission_classes = (AllowAny, )

    def post(self, request, format='json'):
        serializer = CustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        json = serializer.data
        return Response(json, status=status.HTTP_201_CREATED)


class HelloWorldView(APIView):
    permission_classes = (IsAuthenticated, )
    def get(self, request):
        return Response(data={"hello":"world"}, status=status.HTTP_200_OK)

class UserViewSet(mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    """User viewsets"""
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserModelSerializer
    lookup_field = 'username'

    def get_permissions(self):
        permissions = []
        if self.action in ['update']:
            permissions.append(IsAuthenticated)
            permissions.append(IsProfileOwner)
        if self.action == 'follow_unfollow':
            permissions.append(IsAuthenticated)
        return [permission() for permission in permissions]


    @action(detail=False, methods=['post'])
    def signup(self, request):
        """User signup"""
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserModelSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def tweets(self,  request, *args, **kwargs):
        """List of tweets"""
        user = self.get_object()
        queryset = Tweet.objects.filter(user=user)
        page = self.paginate_queryset(queryset)
        serializer = BasicTweetSerializer(
            page, 
            many=True,
            context={
                'user': request.user
            }
        )
        result = self.get_paginated_response(serializer.data)
        data = result.data

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def follow_unfollow(self, request, *args, **kwargs):
        siguiendo = self.get_object()
        context = {
            'siguiendo': siguiendo,
            'request': request
        }
        serializer = FollowUnfollowUserSerializer(
            data=request.data,
            context=context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({}, status=status.HTTP_200_OK)   

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserProfileModelSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    


    