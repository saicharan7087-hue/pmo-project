from django.urls import path
from .views import employee_list_api, login_view,get_employee_by_id,update_employee

urlpatterns = [
    path('employee_list/', employee_list_api, name='employee_list_api'),
    path('login/', login_view, name='login'),
    path('employee/<int:employee_id>/', get_employee_by_id, name='get_employee_by_id'),
    path('update_employee/<str:name>/', update_employee, name='update_employee'),
]
