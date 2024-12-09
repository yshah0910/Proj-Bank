from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse  # Ensure reverse is imported
from bank.bankk.models import Customer, Employee, Branch, Transaction, Dependent, CustomerAccount, Loan, Savings, Checking, Account
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.db import transaction
import random



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

from django.shortcuts import render, redirect, get_object_or_404
from bank.bankk.models import Customer, Branch, Account
from django.db import transaction
import random


def signup_view(request):
    if request.method == 'POST':
        ssn = request.POST.get('ssn')
        name = request.POST.get('name')
        apt_no = request.POST.get('apt_no')
        street_no = request.POST.get('street_no')
        state = request.POST.get('state')
        city = request.POST.get('city')
        zip_code = request.POST.get('zip')
        branch_id = request.POST.get('branch_id_customer_signup')
        account_type = request.POST.get('acc_type')

        # Validate input
        if not all([ssn, name, apt_no, street_no, state, city, zip_code, branch_id, account_type]):
            return render(request, 'login.html', {
                'error': 'All fields are required for signup.',
                'branches': Branch.objects.all()
            })

        try:
            # Validate numeric fields
            ssn = int(ssn)
            apt_no = int(apt_no)
            street_no = int(street_no)
            zip_code = int(zip_code)
            branch_id = int(branch_id)
        except ValueError:
            return render(request, 'login.html', {
                'error': 'SSN, Apartment Number, Street Number, ZIP Code, and Branch ID must be valid numbers.',
                'branches': Branch.objects.all()
            })

        branch = Branch.objects.filter(branch_id=branch_id).first()
        if not branch:
            return render(request, 'login.html', {
                'error': 'Branch ID does not exist.',
                'branches': Branch.objects.all()
            })

        # Transaction to insert into CUSTOMER and ACCOUNT
        try:
            with transaction.atomic():
                # Create the Customer record
                customer = Customer.objects.create(
                    ssn=ssn,
                    name=name,
                    apt_no=apt_no,
                    street_no=street_no,
                    state=state,
                    city=city,
                    zip=zip_code,
                    branch_id=branch_id,
                    e_ssn=None  # Assuming no assigned employee for now
                )

                # Generate a random account number
                account_no = random.randint(1000000000, 9999999999)

                # Create the Account record
                Account.objects.create(
                    account_no=account_no,
                    balance=0.0,  # Default initial balance
                    branch_id=branch_id,
                    acc_type=account_type
                )

            return redirect('login_view')
        except Exception as e:
            return render(request, 'login.html', {
                'error': f'An error occurred while creating the account: {str(e)}',
                'branches': Branch.objects.all()
            })

    # Render the signup form with available branches
    branches = Branch.objects.all()
    return render(request, 'login.html', {'branches': branches})

def customer_dashboard(request, ssn):
    print(f"Loading dashboard for customer SSN: {ssn}")

    # Fetch customer details
    customer = get_object_or_404(Customer, ssn=ssn)

    # Fetch last transaction
    last_transaction = (
        Transaction.objects.filter(account_no__customeraccount__ssn=customer)
        .order_by('-trans_date')
        .first()
    )

    # Branch address
    branch_address = customer.branch.address if customer.branch else "No branch assigned"

    # Determine account type based on related account
    account = CustomerAccount.objects.filter(ssn=customer).first()
    account_type = None
    if account:
        if Loan.objects.filter(account_no=account.account_no).exists():
            account_type = "Loan Account"
        elif Savings.objects.filter(account_no=account.account_no).exists():
            account_type = "Savings Account"
        elif Checking.objects.filter(account_no=account.account_no).exists():
            account_type = "Checking Account"
        else:
            account_type = "Unknown Account Type"

    # Associated employee
    associated_employee = customer.e_ssn.name if customer.e_ssn else "No assigned employee"

    # Fetch all transactions
    transactions = Transaction.objects.filter(account_no__customeraccount__ssn=customer)

    # Context for template
    context = {
        'customer': customer,
        'last_transaction': last_transaction,
        'branch_address': branch_address,
        'account_type': account_type,
        'associated_employee': associated_employee,
        'transactions': transactions,
    }

    return render(request, 'customer_dashboard.html', context)

def employee_dashboard(request, ssn):
    # Fetch employee details
    employee = get_object_or_404(Employee, ssn=ssn)

    # Fetch branch name
    branch_name = employee.branch.name if employee.branch else "No branch assigned"

    # Fetch manager name
    manager_name = employee.manager_ssn.name if employee.manager_ssn else "No manager assigned"

    # Fetch all customers assigned to this employee
    customers = Customer.objects.filter(e_ssn=employee)

    # Prepare customer details
    customer_details = []
    for customer in customers:
        account = CustomerAccount.objects.filter(ssn=customer).first()
        if account:
            account_type = None
            if Loan.objects.filter(account_no=account.account_no).exists():
                account_type = "Loan Account"
            elif Savings.objects.filter(account_no=account.account_no).exists():
                account_type = "Savings Account"
            elif Checking.objects.filter(account_no=account.account_no).exists():
                account_type = "Checking Account"
            else:
                account_type = "Unknown Account Type"

            last_transaction = (
                Transaction.objects.filter(account_no=account.account_no)
                .order_by('-trans_date')
                .first()
            )
            last_activity = last_transaction.trans_date if last_transaction else "No activity"
        else:
            account_type = "No account"
            last_activity = "No activity"

        customer_details.append({
            'name': customer.name,
            'account_type': account_type,
            'last_activity': last_activity,
        })

    # Fetch dependents
    dependents = Dependent.objects.filter(essn=employee)

    # Context for template
    context = {
        'employee': employee,
        'branch_name': branch_name,
        'manager_name': manager_name,
        'customer_details': customer_details,
        'dependents': dependents,
    }

    return render(request, 'employee_dashboard.html', context)

def branch_dashboard(request, branch_id):
    # Fetch branch details
    branch = get_object_or_404(Branch, branch_id=branch_id)

    # Fetch employees working in this branch
    employees = Employee.objects.filter(branch=branch)

    # Prepare customer details with account type and assigned employee
    customer_details = []
    accounts = Account.objects.filter(branch=branch)
    for account in accounts:
        customer_account = CustomerAccount.objects.filter(account_no=account).first()
        if customer_account:
            customer = customer_account.ssn
            assigned_employee = customer.e_ssn.name if customer.e_ssn else "No assigned employee"

            # Determine account type
            if Loan.objects.filter(account_no=account).exists():
                account_type = "Loan Account"
            elif Savings.objects.filter(account_no=account).exists():
                account_type = "Savings Account"
            elif Checking.objects.filter(account_no=account).exists():
                account_type = "Checking Account"
            else:
                account_type = "Unknown Account Type"

            customer_details.append({
                'account_no': account.account_no,
                'customer_name': customer.name,
                'account_type': account_type,
                'assigned_employee': assigned_employee,
            })

    # Context for the template
    context = {
        'branch': branch,
        'employees': employees,
        'customer_details': customer_details,
    }

    return render(request, 'branch_dashboard.html', context)
