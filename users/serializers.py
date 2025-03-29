from rest_framework import serializers
from django.contrib.auth.models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        validators=[]  # You can add custom password validators here if needed
    )
    confirm_password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'email', 
            'password', 
            'confirm_password', 
        ]
        extra_kwargs = {
            'email': {'required': True},
        }
    
    def validate(self, attrs):
        # Validate password match
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        
        # Optional: Add additional validation
        if not attrs.get('email'):
            raise serializers.ValidationError(
                {"email": "Email is required."}
            )
        
        return attrs
    
    def create(self, validated_data):
        # Create user using create_user method to properly hash password
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'email', 
        ]
        read_only_fields = ['id', 'username', 'email']