from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Employee,PassType,EndClient,MainClient

from .serializers import    EmployeeSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate


@api_view(['GET'])
def employee_list_api(request):
    employees = Employee.objects.all()
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data)


@csrf_exempt  # <-- important for disabling CSRF (since you're using Postman)
@api_view(['POST'])  # <-- tells Django REST Framework to expect POST requests
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        return Response({"message": "Login successful"})
    else:
        return Response({"message": "Invalid credentials"}, status=400)


@api_view(['GET'])
def get_employee_by_id(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = EmployeeSerializer(employee)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
def update_employee(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = EmployeeSerializer(employee, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Employee details updated successfully',
            'employee': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])
def get_main_accounts(request):
    """
    Returns only main account IDs and names.
    """
    accounts = MainClient.objects.filter(is_active=True).values('id', 'name').order_by('name')
    return Response(list(accounts))

@api_view(['GET'])
def get_end_clients(request, main_client_id=None):
    """
    Returns end clients linked to a selected main client.
    If a main_client_id is given, return active end clients for that main client.
    """
    if main_client_id:
        clients = EndClient.objects.filter(main_client_id=main_client_id, is_active=True).values('id', 'name').order_by('name')
    else:
        clients = EndClient.objects.filter(is_active=True).values('id', 'name').order_by('name')

    return Response(list(clients))
@api_view(['GET'])
def pass_type(request):
    ptype= PassType.objects.filter(is_active=True).values('id','name').order_by('name')
    return Response(list(ptype))







import pandas as pd
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Employee, MainClient, EndClient, MigrantType
from .serializers import EmployeeSerializer


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_employee_excel(request):
    """
    Upload an Excel file and insert employee data into the database.
    Expected Excel columns:
    full_name, email, phone, main_account, end_client, client_account_manager,
    client_account_manager_email, pass_type, date_of_joining, is_active
    """
    try:
        excel_file = request.FILES.get('file')
        if not excel_file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        df = pd.read_excel(excel_file)

        required_columns = [
            'full_name', 'email', 'phone', 'main_account', 'end_client',
            'client_account_manager', 'client_account_manager_email',
            'pass_type', 'date_of_joining'
        ]
        for col in required_columns:
            if col not in df.columns:
                return Response({'error': f'Missing column: {col}'}, status=status.HTTP_400_BAD_REQUEST)

        inserted_records = []

        for _, row in df.iterrows():
            main_client = MainClient.objects.filter(name=row['main_account']).first()
            end_client = EndClient.objects.filter(name=row['end_client']).first()
            pass_type = MigrantType.objects.filter(migrant_name=row['pass_type']).first()

            employee = Employee.objects.create(
                full_name=row['full_name'],
                email=row['email'],
                phone=row['phone'],
                main_account=main_client,
                end_client=end_client,
                client_account_manager=row.get('client_account_manager', ''),
                client_account_manager_email=row.get('client_account_manager_email', ''),
                pass_type=pass_type,
                date_of_joining=row['date_of_joining'],
                is_active=True
            )
            inserted_records.append(employee.id)

        return Response({
            "message": "Employee data uploaded successfully",
            "inserted_count": len(inserted_records)
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def add_employee(request):
    """
    Add an employee using JSON data.
    """
    try:
        data = request.data

        main_client = MainClient.objects.filter(name=data.get('main_account')).first()
        if not main_client:
            return Response({'error': f"Main account '{data.get('main_account')}' not found"}, status=400)

        end_client = EndClient.objects.filter(name=data.get('end_client')).first()
        if not end_client:
            return Response({'error': f"End client '{data.get('end_client')}' not found"}, status=400)

        pass_type = MigrantType.objects.filter(migrant_name=data.get('pass_type')).first()
        if not pass_type:
            return Response({'error': f"Pass type '{data.get('pass_type')}' not found"}, status=400)

        employee = Employee.objects.create(
            full_name=data.get('full_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            main_account=main_client,
            end_client=end_client,
            client_account_manager=data.get('client_account_manager'),
            client_account_manager_email=data.get('client_account_manager_email'),
            pass_type=pass_type,
            date_of_joining=data.get('date_of_joining'),
            is_active=data.get('is_active', True)
        )

        serializer = EmployeeSerializer(employee)
        return Response({
            "message": "Employee added successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







