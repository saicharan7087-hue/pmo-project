from django.urls import path
from .views import employee_list, login_view,add_employee,upload_employee_excel,main_account_list,update_employee,get_end_clients,task_view,pass_type_list
urlpatterns = [

    path('login/', login_view, name='login'),

    path('add_employee/', add_employee, name='add_employee'),
    path('employee_list/', employee_list, name='get_employee_list'),
    path('upload_employee_excel/',upload_employee_excel, name='upload_employee_excel'),
    path('Main_Clients/', main_account_list, name='Main_Clients'),
    path('employees/<int:employee_id>/update/', update_employee, name='update_employee'),
    path('pass_types/',pass_type_list, name='pass_type_list'),


    path('end_clients/', get_end_clients, name='get_all_end_clients'),
    path('end_clients/<int:main_client_id>/', get_end_clients, name='get_end_clients_by_main_client'),
    path('tasks/', task_view, name='task_view'),
]




