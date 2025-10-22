from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Employee,MainAccount,EndClientDetails,PassType

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
    accounts = MainAccount.objects.filter(is_active=True).values('id', 'name').order_by('name')
    return Response(list(accounts))

@api_view(['GET'])
def get_end_clients(request):
    """
    Returns only end client names (list of strings)
    """
    clients = EndClientDetails.objects.filter(is_active=True).values('id','name').order_by('name')
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