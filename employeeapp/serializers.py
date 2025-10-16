from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    main_account = serializers.CharField(source='main_account.name', read_only=True)
    end_client = serializers.CharField(source='end_client.name', read_only=True)
    pass_type_name = serializers.CharField(source='pass_type.migrant_name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'main_account',
            'end_client',
            'client_account_manager',
            'client_account_manager_email',
            'pass_type_name',
            'date_of_joining',
            'is_active',
        ]



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()



class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['name', 'email', 'phone', 'date_of_joining']