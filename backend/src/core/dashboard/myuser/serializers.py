from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from rest_framework import serializers

from core.dashboard.myuser.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'profile_id','profile_tin', 'birth_date',
            'tax_country', 'tax_state', 'address',
            ]
        read_only_fields = ['profile_id']

    def update(self, instance, validated_data):
        """
            Update and return an existing Profile instance,
            given the validated data.
        """
        instance.profile_tin = validated_data.get(
            'profile_tin', instance.profile_tin
            )
        instance.birth_date = validated_data.get(
            'birth_date', instance.birth_date
            )
        instance.tax_country = validated_data.get(
            'tax_country', instance.tax_country
            )
        instance.tax_state = validated_data.get(
            'tax_state', instance.tax_state
        )
        instance.address = validated_data.get(
            'address', instance.address
        )
        instance.save()
        return instance


class AdminUserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)

    username = serializers.CharField(
        required=True,
        help_text='New Username',
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        help_text='Leave empty if no change needed',
        style={'input_type': 'password', 'placeholder': 'Password'}
    )

    class Meta:
        model = User
        fields = [
        'id', 'username', 'is_active', 'password',
        'first_name', 'last_name', 'email', 'profile'
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data['password'] = make_password(
            validated_data.get('password')
            )
        user = User.objects.create_user(validated_data['username'],
            email=validated_data['email'], password=validated_data['password'],
            )
        user.first_name = validated_data['first_name']
        user.last_name = validated_data['last_name']
        user.is_active = validated_data['is_active']
        user.is_superuser = False
        user_id = get_user_model().objects.all().filter(
            username=validated_data['username']
            ).values().first()['id']
        print(f"user_id: {user_id}")
        newprofile_data = validated_data['profile']
        profile_data = {'profile_tin': newprofile_data['profile_tin'],
                        'birth_date': newprofile_data['birth_date'],
                        'tax_country': newprofile_data['tax_country'],
                        'tax_state': newprofile_data['tax_state'],
                        'address': newprofile_data['address']}
        newinstance = Profile.objects.all().filter(
            profile_user=user_id
            ).first()
        print(f"newinstance: {newinstance}\nprofile_data: {profile_data}")
        ProfileSerializer.update(self,
            instance=newinstance, validated_data=profile_data
            )
        user.save()
        return user

    def update(self, instance, validated_data):
        """
            Update and return an existing User and Profile instance,
            given the validated data.
        """
        instance.first_name = validated_data.get(
            'first_name', instance.first_name
            )
        instance.last_name = validated_data.get(
            'last_name', instance.last_name
            )
        instance.email = validated_data.get('email', instance.email)

        user = User.objects.all().filter(username=instance)
        user_id = user.values().first()['id']
        newinstance = Profile.objects.all().filter(
            profile_user=user_id
            ).first()
        newprofile_data = validated_data['profile']
        profile_data = {'profile_tin': newprofile_data['profile_tin'],
                        'birth_date': newprofile_data['birth_date'],
                        'tax_country': newprofile_data['tax_country'],
                        'tax_state': newprofile_data['tax_state'],
                        'address': newprofile_data['address']}
        ProfileSerializer.update(self,
            instance=newinstance, validated_data=profile_data
            )

        instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=True)
    class Meta:
        model = User
        fields = [
        'username', 'first_name', 'last_name', 'email', 'profile'
        ]

    def update(self, instance, validated_data):
        return AdminUserProfileSerializer().update(
            instance, validated_data
            )
