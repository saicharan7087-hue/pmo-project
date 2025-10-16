from django.urls import path
from .views import employee_list_api, login_view

urlpatterns = [
    path('employee_list/', employee_list_api, name='employee_list_api'),
    path('login/', login_view, name='login'),
]
