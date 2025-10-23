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
from .serializers import EmployeeSerializer


@api_view(['GET'])
def employee_list_api(request):
    employees = Employee.objects.select_related('main_account', 'end_client').all()
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



class AddEmployeeAPIView(APIView):
    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Employee added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





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
    """
    try:
        excel_file = request.FILES.get('file')
        if not excel_file:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        # Read Excel file
        df = pd.read_excel(excel_file)

        # Expected columns in Excel file
        required_columns = ['full_name', 'email', 'phone', 'main_account', 'end_client', 'pass_type', 'date_of_joining','client_account_manager','client_account_manager_email']
        for col in required_columns:
            if col not in df.columns:
                return Response({'error': f'Missing required column: {col}'}, status=status.HTTP_400_BAD_REQUEST)

        inserted_records = []

        # Iterate over rows and save employees
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
                client_account_manager=client_account_manager,
                client_account_manager_email=client_account_manager_email,
                pass_type=pass_type,
                date_of_joining=row['date_of_joining']
            )
            inserted_records.append(employee.id)

        return Response({
            "message": "Employee data uploaded successfully",
            "inserted_ids": inserted_records,
            "count": len(inserted_records)
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
