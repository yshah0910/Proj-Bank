from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse  # Ensure reverse is imported
from bank.bankk.models import Customer, Employee, Branch, Transaction, Dependent
from django.http import HttpResponseRedirect


def login_view(request):
    if request.method == 'POST':
        login_type = request.POST.get('login_type')
        print(f"Login Type: {login_type}")
        print(f"POST Data: {request.POST}")
        if login_type == 'customer':
            ssn = request.POST.get('ssn')
            name = request.POST.get('name')

            # Validate input
            if not ssn or not name:
                return render(request, 'login.html', {'error': 'SSN and Name are required for customer login.'})

            try:
                ssn = int(ssn)  # Ensure SSN is an integer
            except ValueError:
                return render(request, 'login.html', {'error': 'SSN must be a valid number.'})

            # Query the database
            customer = Customer.objects.filter(ssn=ssn, name__iexact=name.strip()).first()

            if customer:
                # Generate the correct URL
                dashboard_url = reverse('customer_dashboard', kwargs={'ssn': customer.ssn})
                print(f"Redirecting to: {dashboard_url}")

                return HttpResponseRedirect(dashboard_url)  # Explicitly redirect to the generated URL

            else:
                print("Customer not found or invalid credentials.")

        elif login_type == 'employee':
            ssn = request.POST.get('ssn')
            name = request.POST.get('name')

            # Validate input
            if not ssn or not name:
                return render(request, 'login.html', {'error': 'SSN and Name are required for employee login.'})

            employee = Employee.objects.filter(ssn=ssn, name=name.strip()).first()

            if employee:
                dashboard_url = reverse('employee_dashboard', kwargs={'ssn': employee.ssn})
                print(f"Redirecting to: {dashboard_url}")
                return redirect(dashboard_url)
            else:
                return render(request, 'login.html', {'error': 'Invalid employee credentials.'})

        elif login_type == 'branch':
            branch_id = request.POST.get('branch_id')
            mgr_ssn = request.POST.get('mgr_ssn')

            # Validate input
            if not branch_id or not mgr_ssn:
                return render(request, 'login.html', {'error': 'Branch ID and Manager SSN are required for branch login.'})

            try:
                mgr_ssn = int(mgr_ssn)  # Ensure Manager SSN is an integer
            except ValueError:
                return render(request, 'login.html', {'error': 'Manager SSN must be a valid number.'})

            branch = Branch.objects.filter(branch_id=branch_id, mgr_ssn=mgr_ssn).first()

            if branch:
                dashboard_url = reverse('branch_dashboard', kwargs={'branch_id': branch.branch_id})
                print(f"Redirecting to: {dashboard_url}")
                return redirect(dashboard_url)
            else:
                return render(request, 'login.html', {'error': 'Invalid branch credentials.'})

        # Generic error for invalid login type
        return render(request, 'login.html', {'error': 'Invalid login type selected.'})

    return render(request, 'login.html')


def customer_dashboard(request, ssn):
    print(f"Loading dashboard for customer SSN: {ssn}")
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
