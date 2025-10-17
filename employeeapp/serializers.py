from rest_framework import serializers
from .models import Employee

class EmployeeSerializer(serializers.ModelSerializer):
    # Keep these fields readable for GET responses,
    # but don't block updates to other fields.
    main_account = serializers.CharField(source='main_account.name', read_only=True)
    end_client = serializers.CharField(source='end_client.name', read_only=True)
    pass_type_name = serializers.CharField(source='pass_type.migrant_name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id',
            'full_name',
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

    def update(self, instance, validated_data):
        """Allow partial update of employee details."""
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.date_of_joining = validated_data.get('date_of_joining', instance.date_of_joining)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.client_account_manager= validated_data.get('client_account_manager', instance.client_account_manager)

        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()




