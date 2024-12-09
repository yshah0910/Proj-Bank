from django.urls import path
from bank.bankk import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('customer/<int:ssn>/', views.customer_dashboard, name='customer_dashboard'),
    path('employee/<int:ssn>/', views.employee_dashboard, name='employee_dashboard'),
    path('branch/<int:branch_id>/', views.branch_dashboard, name='branch_dashboard'),
]
