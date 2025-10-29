from rest_framework import serializers
from .models import Employee, MainClient, EndClient, MigrantType,Task


class EmployeeSerializer(serializers.ModelSerializer):
    main_account = serializers.CharField(write_only=True, required=False)
    end_client = serializers.CharField(write_only=True, required=False)
    pass_type = serializers.CharField(write_only=True, required=False)
    main_account_name = serializers.CharField(source='main_account.name', read_only=True)
    end_client_name = serializers.CharField(source='end_client.name', read_only=True)
    pass_type_name = serializers.CharField(source='pass_type.migrant_name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'full_name', 'email', 'phone',
            'main_account', 'main_account_name',
            'end_client', 'end_client_name',
            'pass_type', 'pass_type_name',
            'client_account_manager', 'client_account_manager_email',
            'date_of_joining', 'is_active'
        ]

    #  Duplicate validation logic
    def validate(self, data):
        full_name = data.get('full_name')
        email = data.get('email')
        phone = data.get('phone')

        # During update, ignore the current instance
        instance = getattr(self, 'instance', None)

        # Check duplicate based on name + email + phone
        existing = Employee.objects.filter(
            full_name=full_name, email=email, phone=phone
        )
        if instance:
            existing = existing.exclude(id=instance.id)

        if existing.exists():
            raise serializers.ValidationError(" Employee with the same name, email, and phone already exists.")

        # Check email uniqueness
        email_exists = Employee.objects.filter(email=email)
        if instance:
            email_exists = email_exists.exclude(id=instance.id)
        if email_exists.exists():
            raise serializers.ValidationError(" This email is already registered.")

        # Check phone uniqueness
        phone_exists = Employee.objects.filter(phone=phone)
        if instance:
            phone_exists = phone_exists.exclude(id=instance.id)
        if phone_exists.exists():
            raise serializers.ValidationError(" This phone number is already registered.")

        return data

    # Create or update helper
    def create_or_update_employee(self, validated_data, instance=None):
        main_account_name = validated_data.pop('main_account', None)
        end_client_name = validated_data.pop('end_client', None)
        pass_type_name = validated_data.pop('pass_type', None)

        main_account = None
        end_client = None
        pass_type = None


        if main_account_name:
            main_account, _ = MainClient.objects.get_or_create(name=main_account_name)


        if end_client_name:
            if main_account:
                end_client, _ = EndClient.objects.get_or_create(
                    name=end_client_name, main_client=main_account
                )
            else:
                end_client, _ = EndClient.objects.get_or_create(name=end_client_name)


        if pass_type_name:
            pass_type, _ = MigrantType.objects.get_or_create(migrant_name=pass_type_name)


        if instance:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.main_account = main_account
            instance.end_client = end_client
            instance.pass_type = pass_type
            instance.save()
            return instance


        return Employee.objects.create(
            main_account=main_account,
            end_client=end_client,
            pass_type=pass_type,
            **validated_data
        )

    def create(self, validated_data):
        return self.create_or_update_employee(validated_data)

    def update(self, instance, validated_data):
        return self.create_or_update_employee(validated_data, instance)



class MainClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainClient
        fields = ['id', 'name']





class EndClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = EndClient
        fields = ['id', 'name']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name']


class MigrantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MigrantType
        fields = ['id', 'name']


