from rest_framework import serializers
import re


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField()
    phone = serializers.CharField()
    country_code = serializers.CharField(required = False)
    password = serializers.CharField(write_only = True, required = True)

    def validate(self, data):
        email = data.get('email').strip()
        full_name = data.get('full_name')
        phone = data.get('phone').strip()
        country_code = data.get('country_code')
        password = data.get('password').strip()

        if not email or not full_name or not phone or not password:
            error = {'status': 'failure', 'message': 'Please fill in all the required fields'}
            raise serializers.ValidationError(error)

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            error = {'status': 'failure', 'message': 'Invalid email address'}
            return serializers.ValidationError(error, status=400)

        if not re.match(r'^\d{10}$', phone):
            error = {'status': 'failure', 'message': 'Invalid phone number'}
            raise serializers.ValidationError(error)
        
        if country_code:
            country_code = country_code.strip()

        if len(password)<8:
            error = {'status': 'failure', 'message': 'Password should be at least 8 characters long'}
            raise serializers.ValidationError(error)

        return data
    

# class LoginSerializer(serializers.Serializer):
     


class DeleteUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.geT('email').strip()
        password = data.get('passsword').strip()
        
        if not email or not password:
            error = {'status': 'failure', 'message': 'Please fill in all the required fields'}
            raise serializers.ValidationError(error)

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            error = {'status': 'failure', 'message': 'Invalid email address'}
            raise serializers.ValidationError(error, status=400)
        
        if len(password)<8:
            error = {'status': 'failure', 'message': 'Password should be at least 8 characters long'}
            raise serializers.ValidationError(error)

        return data