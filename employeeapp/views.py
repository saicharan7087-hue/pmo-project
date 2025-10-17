from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Employee
from django.contrib.auth.models import User
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
def get_employee_by_name(request, name):
    # Retrieve employee by name (case-insensitive)
    employee = get_object_or_404(Employee, name__iexact=name)
    serializer = EmployeeSerializer(employee)
    return Response(serializer.data)