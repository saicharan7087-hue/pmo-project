from django.db import models
from django.contrib.auth.models import User

class MainClient(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class EndClient(models.Model):
    name = models.CharField(max_length=100)
    main_client = models.ForeignKey(MainClient, on_delete=models.CASCADE, related_name='end_clients')

    class Meta:
        unique_together = ('name', 'main_client')  # Prevent same end client name under same main client

    def __str__(self):
        return self.name


class MigrantType(models.Model):
    migrant_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.migrant_name


class Employee(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    main_account = models.ForeignKey(MainClient, on_delete=models.SET_NULL, null=True, blank=True)
    end_client = models.ForeignKey(EndClient, on_delete=models.SET_NULL, null=True, blank=True)
    client_account_manager = models.CharField(max_length=100, blank=True, null=True)
    client_account_manager_email = models.EmailField(blank=True, null=True)
    pass_type = models.ForeignKey(MigrantType, on_delete=models.SET_NULL, null=True, blank=True)
    date_of_joining = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('full_name', 'email', 'phone')

    def __str__(self):
        return self.full_name


class Task(models.Model):
    TASK_TYPES = [
        ('Development', 'Development'),
        ('Service', 'Service'),
        ('Error', 'Error'),
    ]

    name = models.CharField(max_length=100, choices=TASK_TYPES, unique=True)

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=100)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='types')

    def __str__(self):
        return self.name




class Timesheet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timesheets')
    month = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.month}"


class Week(models.Model):
    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE, related_name='weeks')
    start_date = models.DateField()
    end_date = models.DateField()
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f"Week: {self.start_date} → {self.end_date}"


class Day(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name='days')
    date = models.DateField()
    day_name = models.CharField(max_length=10)
    is_weekend = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.date} ({self.day_name})"


class TimesheetEntry(models.Model):

    day_index = models.IntegerField(default=0) # 0–6 for Mon–Sun
    hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE)
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=255, default="", blank=True)
    type_name = models.CharField(max_length=255, default="", blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entries', null=True, blank=True)  # ✅ Added to prevent AnonymousUser issues

    def __str__(self):
        return f"{self.task_name} - {self.type_name} ({self.hours} hrs)"



