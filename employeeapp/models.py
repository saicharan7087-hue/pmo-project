from django.db import models

class MainClient(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class EndClient(models.Model):
    name = models.CharField(max_length=100)
    main_client = models.ForeignKey(MainClient, on_delete=models.CASCADE, related_name='end_clients')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class MigrantType(models.Model):
    migrant_name = models.CharField(max_length=50)

    def __str__(self):
        return self.migrant_name


class Employee(models.Model):
    full_name = models.CharField(max_length=100,unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True,unique=True)
    main_account = models.ForeignKey(MainClient, on_delete=models.SET_NULL, null=True, blank=True)
    end_client = models.ForeignKey(EndClient, on_delete=models.SET_NULL, null=True, blank=True)
    client_account_manager = models.CharField(max_length=100, blank=True, null=True)
    client_account_manager_email = models.EmailField(blank=True, null=True)
    pass_type = models.ForeignKey(MigrantType, on_delete=models.SET_NULL, null=True, blank=True)
    date_of_joining = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name


class PassType(models.Model):
    name = models.CharField(max_length=225)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
