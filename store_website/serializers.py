from rest_framework import serializers
import re


class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    full_name = serializers.CharField()
    phone = serializers.CharField()
    country_code = serializers.CharField()
    password = serializers.CharField(write_only = True, required = True)

    def validate(self, data):
        email = data.get('email').strip()
        first_name = data.get('first_name').strip()
        last_name = data.get('last_name').strip()
        phone = data.get('phone').strip()
        country_code = data.get('country_code').strip()
        password = data.get('password').strip()
        confirmpassword = data.get('confirmpassword').strip()

        if not email or not first_name or not last_name or not phone or not password or not confirmpassword:
            error = {'status': 'failure', 'message': 'Please fill in all the required fields'}
            raise serializers.ValidationError(error)

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            error = {'status': 'failure', 'message': 'Invalid email address'}
            return serializers.ValidationError(error, status=400)

        if not re.match(r'^[A-Za-z]{2,}$', first_name):
            error = {'status': 'failure', 'message': 'Invalid first name'}
            raise serializers.ValidationError(error)

        if not re.match(r'^[A-Za-z]{2,}$', last_name):
            error = {'status': 'failure', 'message': 'Invalid last name'}
            raise serializers.ValidationError(error)

        if not re.match(r'^\d{10}$', phone):
            error = {'status': 'failure', 'message': 'Invalid phone number'}
            raise serializers.ValidationError(error)

        if password != confirmpassword:
            error = {'status': 'failure', 'message': 'Passwords do not match'}
            raise serializers.ValidationError(error)

        if len(password)<8:
            error = {'status': 'failure', 'message': 'Password should be at least 8 characters long'}
            raise serializers.ValidationError(error)

        return data