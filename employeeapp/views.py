from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate
import pandas as pd
from .models import Employee, MainClient, EndClient, MigrantType, PassType
from .serializers import EmployeeSerializer

# ---------------- Employee List ----------------
@api_view(['GET'])
def employee_list_api(request):
    employees = Employee.objects.select_related('main_account', 'end_client', 'pass_type').all()
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data)

# ---------------- Employee Login ----------------
@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        return Response({"message": "Login successful"})
    return Response({"message": "Invalid credentials"}, status=400)

# ---------------- Get Employee By ID ----------------
@api_view(['GET'])
def get_employee_by_id(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = EmployeeSerializer(employee)
    return Response(serializer.data)

# ---------------- Update Employee ----------------
@api_view(['PUT'])
def update_employee(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = EmployeeSerializer(employee, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Employee updated successfully', 'employee': serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------- Main Accounts ----------------
@api_view(['GET'])
def get_main_accounts(request):
    accounts = MainClient.objects.filter(is_active=True).values('id', 'name').order_by('name')
    return Response(list(accounts))

# ---------------- End Clients ----------------
@api_view(['GET'])
def get_end_clients(request, main_client_id=None):
    if main_client_id:
        clients = EndClient.objects.filter(main_client_id=main_client_id, is_active=True).values('id', 'name').order_by('name')
    else:
        clients = EndClient.objects.filter(is_active=True).values('id', 'name').order_by('name')
    return Response(list(clients))

# ---------------- Pass Types ----------------
@api_view(['GET'])
def pass_type(request):
    types = PassType.objects.filter(is_active=True).values('id', 'name').order_by('name')
    return Response(list(types))

# ---------------- Add Employee API ----------------
class AddEmployeeAPIView(APIView):
    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Employee added successfully", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)

# ---------------- Upload Employee Excel ----------------
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_employee_excel(request):
    excel_file = request.FILES.get('file')
    if not excel_file:
        return Response({'error': 'No file uploaded. Use key "file".'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        df = pd.read_excel(excel_file)

        required_columns = ['full_name', 'email', 'phone', 'main_account', 'end_client', 'pass_type', 'date_of_joining', 'client_account_manager', 'client_account_manager_email']
        for col in required_columns:
            if col not in df.columns:
                return Response({'error': f'Missing required column: {col}'}, status=status.HTTP_400_BAD_REQUEST)

        inserted_ids = []
        for _, row in df.iterrows():
            serializer = EmployeeSerializer(data=row.to_dict())
            if serializer.is_valid():
                employee = serializer.save()
                inserted_ids.append(employee.id)
            else:
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Employees uploaded successfully', 'inserted_ids': inserted_ids}, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
