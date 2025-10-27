from rest_framework import serializers
from .models import Employee, MainClient, EndClient, MigrantType

class MainClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainClient
        fields = ['id', 'name', 'is_active']


class EndClientSerializer(serializers.ModelSerializer):
    main_client = MainClientSerializer(read_only=True)

    class Meta:
        model = EndClient
        fields = ['id', 'name', 'is_active', 'main_client']


from rest_framework import serializers
from .models import Employee, MainClient, EndClient, MigrantType

class EmployeeSerializer(serializers.ModelSerializer):
    main_account = serializers.CharField(source='main_account.name', read_only=True)
    end_client = serializers.CharField(source='end_client.name', read_only=True)
    pass_type = serializers.CharField(source='pass_type.migrant_name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'full_name', 'email', 'phone',
            'main_account', 'end_client',
            'client_account_manager', 'client_account_manager_email',
            'pass_type', 'date_of_joining', 'is_active'
        ]

    def create(self, validated_data):
        main_account_name = validated_data.pop('main_account', None)
        end_client_name = validated_data.pop('end_client', None)
        pass_type_value = validated_data.pop('pass_type', None)

        main_account = None
        end_client = None
        pass_type = None

        if main_account_name:
            main_account, _ = MainClient.objects.get_or_create(name=main_account_name)

        if end_client_name:
            end_client, _ = EndClient.objects.get_or_create(name=end_client_name, main_client=main_account)

        if pass_type_value:
            if pass_type_value.isdigit():
                pass_type = MigrantType.objects.filter(id=int(pass_type_value)).first()
            else:
                pass_type, _ = MigrantType.objects.get_or_create(migrant_name=pass_type_value)

        employee = Employee.objects.create(
            main_account=main_account,
            end_client=end_client,
            pass_type=pass_type,
            **validated_data
        )
        return employee

    def update(self, instance, validated_data):
        """Allow partial update of employee details."""
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.date_of_joining = validated_data.get('date_of_joining', instance.date_of_joining)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.client_account_manager = validated_data.get('client_account_manager', instance.client_account_manager)
        instance.client_account_manager_email = validated_data.get('client_account_manager_email', instance.client_account_manager_email)

        main_account_name = validated_data.get('main_account')
        end_client_name = validated_data.get('end_client')
        pass_type_value = validated_data.get('pass_type')

        if main_account_name:
            instance.main_account, _ = MainClient.objects.get_or_create(name=main_account_name)

        if end_client_name:
            instance.end_client, _ = EndClient.objects.get_or_create(name=end_client_name, main_client=instance.main_account)

        if pass_type_value:
            if pass_type_value.isdigit():
                instance.pass_type = MigrantType.objects.filter(id=int(pass_type_value)).first()
            else:
                instance.pass_type, _ = MigrantType.objects.get_or_create(migrant_name=pass_type_value)

        instance.save()
        return instance