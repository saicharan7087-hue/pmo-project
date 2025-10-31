from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, parser_classes,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny
from django.db.models import Q
from rest_framework.authtoken.models import Token
from django.utils import timezone

from datetime import datetime, timedelta
import pandas as pd
from .models import Employee, MainClient, EndClient, MigrantType,Task,Type,User, Timesheet,Week,TimesheetEntry
from .serializers import EmployeeSerializer, MainClientSerializer, EndClientSerializer,TaskSerializer,MigrantTypeSerializer,TypeSerializer,TimesheetSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # Authenticate user
    user = authenticate(username=username, password=password)

    if user:
        # ✅ Return clean JSON structure
        return Response({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,

            }
        }, status=status.HTTP_200_OK)

    #  Invalid login
    return Response({
        "message": "Invalid credentials"
    }, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def add_employee(request):
    """
    Add a new employee.
    Accepts main_account and end_client as IDs from frontend.
    Returns names instead of IDs in response.
    """
    data = request.data.copy()

    # Get IDs
    main_account_id = data.get('main_account')
    end_client_id = data.get('end_client')
    pass_type_id = data.get('pass_type')

    main_account = MainClient.objects.filter(id=main_account_id).first() if main_account_id else None
    end_client = EndClient.objects.filter(id=end_client_id).first() if end_client_id else None
    pass_type = MigrantType.objects.filter(id=pass_type_id).first() if pass_type_id else None

    # Prevent duplicate employee
    if Employee.objects.filter(
        full_name__iexact=data.get('full_name'),
        email__iexact=data.get('email'),
        phone=data.get('phone')
    ).exists():
        return Response({"error": "Employee with same name, email or phone already exists"},
                        status=status.HTTP_400_BAD_REQUEST)

    # Create employee
    employee = Employee.objects.create(
        full_name=data.get('full_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        main_account=main_account,
        end_client=end_client,
        client_account_manager=data.get('client_account_manager'),
        client_account_manager_email=data.get('client_account_manager_email'),
        pass_type=pass_type,
        date_of_joining=data.get('date_of_joining'),
        is_active=data.get('is_active', True)
    )

    serializer = EmployeeSerializer(employee)
    return Response({"message": "Employee added successfully", "data": serializer.data},
                    status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def update_employee(request, employee_id):
    """
    Update an existing employee using either IDs or names.
    Always returns names in response.
    """
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data.copy()

    # Resolve relationships
    main_account = None
    if data.get('main_account'):
        if str(data['main_account']).isdigit():
            main_account = MainClient.objects.filter(id=data['main_account']).first()
        else:
            main_account = MainClient.objects.filter(name=data['main_account']).first()

    end_client = None
    if data.get('end_client'):
        if str(data['end_client']).isdigit():
            end_client = EndClient.objects.filter(id=data['end_client']).first()
        else:
            end_client = EndClient.objects.filter(name=data['end_client']).first()

    pass_type = None
    if data.get('pass_type'):
        if str(data['pass_type']).isdigit():
            pass_type = MigrantType.objects.filter(id=data['pass_type']).first()
        else:
            pass_type = MigrantType.objects.filter(migrant_name=data['pass_type']).first()

    # Update fields
    employee.full_name = data.get('full_name', employee.full_name)
    employee.email = data.get('email', employee.email)
    employee.phone = data.get('phone', employee.phone)
    employee.client_account_manager = data.get('client_account_manager', employee.client_account_manager)
    employee.client_account_manager_email = data.get('client_account_manager_email', employee.client_account_manager_email)
    employee.date_of_joining = data.get('date_of_joining', employee.date_of_joining)
    employee.is_active = data.get('is_active', employee.is_active)
    employee.main_account = main_account
    employee.end_client = end_client
    employee.pass_type = pass_type
    employee.save()

    serializer = EmployeeSerializer(employee)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def employee_list(request):
    employees = Employee.objects.all().order_by('id')
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_employee_excel(request):
    excel_file = request.FILES.get('file')
    if not excel_file:
        return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        df = pd.read_excel(excel_file)

        required_columns = [
            'full_name', 'email', 'phone', 'main_account', 'end_client',
            'pass_type', 'client_account_manager', 'client_account_manager_email',
            'date_of_joining'
        ]
        for col in required_columns:
            if col not in df.columns:
                return Response({'error': f'Missing required column: {col}'}, status=status.HTTP_400_BAD_REQUEST)

        inserted, skipped = [], []

        for _, row in df.iterrows():
            full_name = str(row['full_name']).strip()
            email = str(row['email']).strip().lower()
            phone = str(row['phone']).strip()


            if Employee.objects.filter(
                Q(full_name__iexact=full_name) | Q(email__iexact=email) | Q(phone__iexact=phone)
            ).exists():
                skipped.append(full_name)
                continue

            main_account, _ = MainClient.objects.get_or_create(name=row['main_account'])
            end_client, _ = EndClient.objects.get_or_create(name=row['end_client'], main_client=main_account)
            pass_type, _ = MigrantType.objects.get_or_create(migrant_name=row['pass_type'])

            Employee.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                main_account=main_account,
                end_client=end_client,
                client_account_manager=row['client_account_manager'],
                client_account_manager_email=row['client_account_manager_email'],
                pass_type=pass_type,
                date_of_joining=row['date_of_joining'],
            )
            inserted.append(full_name)

        return Response({
            "message": " Excel upload complete",
            "inserted_count": len(inserted),
            "skipped_duplicates": len(skipped),
            "inserted": inserted,
            "skipped": skipped
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_end_clients(request, main_client_id=None):
    """
    Get End Clients. If main_client_id is provided, filter by that main client.
    Example:
    /end_clients/          → returns all end clients
    /end_clients/1/        → returns only end clients of main_client_id = 1
    """
    if main_client_id:
        end_clients = EndClient.objects.filter(main_client_id=main_client_id)
    else:
        end_clients = EndClient.objects.all()

    serializer = EndClientSerializer(end_clients, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['GET'])
def main_account_list(request):
    main_clients = MainClient.objects.all().order_by('id')
    serializer = MainClientSerializer(main_clients, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET', 'POST'])
def task_view(request):
    """
    GET  → Return all tasks (Development, Service, Error)
    POST → Add a new task type (optional)
    """

    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Task added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # If GET request, return all task types
    tasks = Task.objects.all().order_by('id')
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_types_by_task(request, task_id):
    types = Type.objects.filter(task_id=task_id)
    serializer = TypeSerializer(types, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def pass_type_list(request):
    """
    Get all available Pass Types (Migrant Types)
    Example: /api/passtypes/
    """
    pass_types = MigrantType.objects.all().order_by('id')
    serializer = MigrantTypeSerializer(pass_types, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_employee_by_id(request, employee_id):
    """
    Get employee details by ID
    Example: /api/employees/5/
    """
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response(
            {"error": f"Employee with ID {employee_id} not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = EmployeeSerializer(employee)
    return Response(serializer.data, status=status.HTTP_200_OK)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from .models import Timesheet, Week, Task, Type, TimesheetEntry

@api_view(['POST'])
@permission_classes([AllowAny])
def save_timesheet(request):
    try:
        data = request.data

        user_id = data.get("user_id")
        month = data.get("month")
        weeks = data.get("weeks", [])

        if not user_id or not month:
            return Response({"error": "user_id and month are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Create or update timesheet
        timesheet, _ = Timesheet.objects.get_or_create(user=user, month=month)
        timesheet.weeks.all().delete()  # clear previous data

        for week_data in weeks:
            start_date = week_data.get("startDate")
            end_date = week_data.get("endDate")
            tasks = week_data.get("tasks", [])

            week = Week.objects.create(
                timesheet=timesheet,
                start_date=start_date,
                end_date=end_date,
            )

            for task_data in tasks:
                task_name = task_data.get("task")
                type_name = task_data.get("type")
                hours_data = task_data.get("hours", [])

                # Get or create Task and Type
                task_obj, _ = Task.objects.get_or_create(name=task_name)
                type_obj, _ = Type.objects.get_or_create(name=type_name, task=task_obj)

                # Calculate total hours
                total_hours = sum(float(h or 0) for h in hours_data)

                # Create TimesheetEntry
                TimesheetEntry.objects.create(
                    timesheet=timesheet,
                    week=week,
                    task=task_obj,
                    type=type_obj,
                    hours=total_hours
                )

        return Response({"message": "Timesheet saved successfully"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

