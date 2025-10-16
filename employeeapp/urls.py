from django.urls import path
from . import views

urlpatterns = [
    path('employee_list/', views.employee_list_api, name='employee_list_api'),
]
