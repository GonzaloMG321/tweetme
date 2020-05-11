# Django
from  django.urls import path, include

# Django rest framework
from rest_framework.routers import DefaultRouter

# Views
from .views import TweetViewSet

# JWT
from rest_framework_simplejwt import views as jwt_views

router = DefaultRouter()
router.register(r'tweets',TweetViewSet, basename='tweets')

urlpatterns = [
    path('', include(router.urls))
]