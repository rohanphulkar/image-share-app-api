from rest_framework import serializers
from .models import Account,SharedFile
from django.core.validators import MinLengthValidator


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Account
        fields = ['email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        account = Account(
            email=self.validated_data['email'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password', 'Passwords must match'})
        account.set_password(password)
        account.save()
        return account

class SharedFileAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedFile
        fields = ['file','link','date','file_name','file_type','file_size']

class SharedFileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_owner_name')
    email = serializers.SerializerMethodField('get_owner_email')
    class Meta:
        model = SharedFile
        fields = ['file','link','date','owner','name','email','file_name','file_type','file_size','expires_on']
    
    def get_owner_email(self,obj):
        return obj.owner.email

    def get_owner_name(self,obj):
        return obj.owner.name