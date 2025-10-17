from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Employee
from .serializers import  LoginSerializer,  EmployeeSerializer
from django.shortcuts import get_object_or_404


@api_view(['GET'])
def employee_list_api(request):
    employees = Employee.objects.all()
    serializer = EmployeeSerializer(employees, many=True)
    return Response(serializer.data)


@csrf_exempt  # <-- important for disabling CSRF (since you're using Postman)
@api_view(['POST'])  # <-- tells Django REST Framework to expect POST requests
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(username=username, password=password)
            return Response({"message": "Login successful"})
        except User.DoesNotExist:
            return Response({"message": "Invalid credentials"}, status=400)

    return Response(serializer.errors, status=400)


@api_view(['GET'])
def get_employee_by_name(request, name):
    # Retrieve employee by name (case-insensitive)
    employee = get_object_or_404(Employee, name__iexact=name)
    serializer = EmployeeSerializer(employee)
    return Response(serializer.data)