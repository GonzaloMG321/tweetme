"""User serializers"""
# Django
from django.contrib.auth import password_validation

# Django REST Framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# Jwt
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Model
from users.models import User, Profile

# Serializers
from users.serializers.profiles import ProfileModelSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        token['nombre'] = user.nombre
        token['a_paterno'] = user.apellido_paterno
        token['username'] = user.username
        return token


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'nombre', 'apellido_paterno']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, data):
        password = data.pop('password', None)

        instance = self.Meta.model(**data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class UserModelSerializer(serializers.ModelSerializer):
    profile = ProfileModelSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'username', 'profile']


class UserProfileInformationSerializer(serializers.ModelSerializer):
    follow_account = serializers.SerializerMethodField(read_only=True)
    profile = ProfileModelSerializer(read_only=True)
    
    class Meta(UserModelSerializer.Meta):
        fields = UserModelSerializer.Meta.fields + ['profile', 'follow_account']
    
    def get_follow_account(self, obj):
        siguiendo = obj
        seguidor = self.context['user']
        if not seguidor.is_anonymous:
            qs = Seguidor.objects.filter(seguidor=seguidor, siguiendo=siguiendo)
            return qs.exists()
        return False


class UserSignUpSerializer(serializers.Serializer):
    """User create serializer"""
    username = serializers.CharField(
        min_length=4,
        max_length=20,
        validators= [
            UniqueValidator(
                queryset=User.objects.all(),
                message='Ya existe un usuario con este nombre'
            )
        ]
    )

    email = serializers.EmailField(
        validators= [
            UniqueValidator(
                queryset= User.objects.all(),
                message= 'Email ya registrado'
            )
        ]
    )

    nombre = serializers.CharField(min_length=2, max_length=30)
    apellido_paterno=serializers.CharField(min_length=2, max_length=30)
    apellido_materno=serializers.CharField(min_length=2, max_length=30, required=False)
    password = serializers.CharField(min_length=8, max_length=60)
    password_confirmation = serializers.CharField(min_length=8, max_length=60)

    def validate(self, data):
        passwd = data['password']
        passwd_conf = data['password_confirmation']

        if passwd != passwd_conf:
            raise serializers.ValidationError('Las contraseñas no coinciden')
        
        password_validation.validate_password(passwd)
        return data


    def create(self, data):
        data.pop('password_confirmation')
        user = User.objects.create_user(**data)
        Profile.objects.create(user=user)
        return user


class UserProfileModelSerializer(serializers.ModelSerializer):
    profile = ProfileModelSerializer(read_only=True)
    biografia = serializers.CharField(required=False, write_only=True)
    picture = serializers.ImageField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ['nombre', 'apellido_paterno', 'apellido_materno', 'profile', 'biografia', 'picture']

    def update(self, instance, data):
        profile = instance.profile
        profile.biografia = data.get('biografia', '')

        if 'picture' in data:
            profile.picture = data['picture']
        profile.save()
        return super(UserProfileModelSerializer, self).update(instance, data)

class FollowUnfollowUserSerializer(serializers.Serializer):
    action = serializers.CharField()
    seguidor = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_action(self, value):
        options = ['follow', 'unfollow']
        if not value in options:
            raise serializers.ValidationError('La acción enviada no es válida')
        return value

    def validate_seguidor(self, seguidor):
        siguiendo = self.context['siguiendo']
        
        if siguiendo == seguidor:
            raise serializers.ValidationError('No puedes seguir o dejar de seguir tu propio perfil')
        return seguidor

    def validate(self, data):
        siguiendo = self.context['siguiendo']
        profile = siguiendo.profile
        me = data['seguidor']
        opcion = data['action']
        
        qs = profile.followers.filter(username=me.username)
        print(qs.exists())
        print(opcion)
        if opcion == 'follow':
            if qs.exists():
                raise serializers.ValidationError('Ya sigues a este usuario')
        else:
            if not qs.exists():
                raise serializers.ValidationError('No sigues a este usuario')
        return data

    def create(self, data):
        siguiendo = self.context['siguiendo']
        me = data['seguidor']
        profile = siguiendo.profile
        action = data['action']

        if action == 'follow':
            """seguidor_siguiendo = Seguidor.objects.create(
                seguidor=seguidor,
                siguiendo=siguiendo
            )"""
            profile.followers.add(me)
        else:
            """ 
            seguidor_siguiendo = Seguidor.objects.filter(
                seguidor=seguidor,
                siguiendo=siguiendo
            )"""
            # seguidor_siguiendo.delete()
            profile.followers.remove(me)
        return data



