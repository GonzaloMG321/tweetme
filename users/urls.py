# Django
from  django.urls import path, include

# DJango Rest Framework
from rest_framework.routers import DefaultRouter

# JWT
from rest_framework_simplejwt import views as jwt_views

# Views
from .views import ObtainTokenPairWithColorView, CustomUserCreate, HelloWorldView,UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('login/', ObtainTokenPairWithColorView.as_view(), name='token_create'),  
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]


