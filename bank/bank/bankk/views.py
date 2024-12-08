from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from bank.bankk.models import Customer, Employee, Branch, Transaction, Dependent

def login_view(request):
    if request.method == 'POST':
        login_type = request.POST['login_type']
        if login_type == 'customer':
            ssn = request.POST['ssn']
            name = request.POST['name']
            customer = Customer.objects.filter(ssn=ssn, name=name).first()
            if customer:
                return redirect('customer_dashboard', ssn=customer.ssn)
        elif login_type == 'employee':
            ssn = request.POST['ssn']
            name = request.POST['name']
            employee = Employee.objects.filter(ssn=ssn, name=name).first()
            if employee:
                return redirect('employee_dashboard', ssn=employee.ssn)
        elif login_type == 'branch':
            branch_id = request.POST['branch_id']
            mgr_ssn = request.POST['mgr_ssn']
            branch = Branch.objects.filter(branch_id=branch_id, mgr_ssn=mgr_ssn).first()
            if branch:
                return redirect('branch_dashboard', branch_id=branch.branch_id)
    return render(request, 'login.html')

def customer_dashboard(request, ssn):
    customer = get_object_or_404(Customer, ssn=ssn)
    transactions = Transaction.objects.filter(account_no__customeraccount__ssn=customer)
    return render(request, 'customer_dashboard.html', {'customer': customer, 'transactions': transactions})

def employee_dashboard(request, ssn):
    employee = get_object_or_404(Employee, ssn=ssn)
    customers = Customer.objects.filter(e_ssn=employee)
    dependents = Dependent.objects.filter(essn=employee)
    return render(request, 'employee_dashboard.html', {'employee': employee, 'customers': customers, 'dependents': dependents})

def branch_dashboard(request, branch_id):
    branch = get_object_or_404(Branch, branch_id=branch_id)
    return render(request, 'branch_dashboard.html', {'branch': branch})
