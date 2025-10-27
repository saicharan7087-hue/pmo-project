from django.urls import path
from .views import employee_list_api, login_view,get_employee_by_id,update_employee,get_main_accounts,get_end_clients,pass_type,add_employee,upload_employee_excel

urlpatterns = [
    path('employee_list/', employee_list_api, name='employee_list_api'),
    path('login/', login_view, name='login'),
    path('employee/<int:employee_id>/', get_employee_by_id, name='get_employee_by_id'),
    path('update_employee/<int:employee_id>/', update_employee, name='update_employee'),
    path('main_accounts/', get_main_accounts, name='get_main_accounts'),
    path('api/end_clients/<int:main_client_id>/', get_end_clients, name='get_end_clients_by_main'),
    path('pass_type/', pass_type, name='pass_type'),
    path('add_employee/', add_employee, name='add_employee'),
    path('api/upload_employees/', upload_employee_excel),

]