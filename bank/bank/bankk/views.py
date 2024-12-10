from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from bank.bankk.models import Customer, Employee, Branch, Transaction, Dependent, CustomerAccount, Loan, Savings, Checking, Account
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.db import transaction
import random
from django.utils import timezone
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt



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

        if not all([ssn, name, apt_no, street_no, state, city, zip_code, branch_id, account_type]):
            return render(request, 'login.html', {
                'error': 'All fields are required for signup.',
                'branches': Branch.objects.all()
            })

        try:
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

        try:
            with transaction.atomic():
                customer = Customer.objects.create(
                    ssn=ssn,
                    name=name,
                    apt_no=apt_no,
                    street_no=street_no,
                    state=state,
                    city=city,
                    zip=zip_code,
                    branch_id=branch_id,
                    e_ssn=None
                )

                next_account_no = get_next_account_no()

                account = Account.objects.create(
                    account_no=next_account_no,
                    balance=0.0,
                    branch_id=branch_id,
                    acc_type=account_type
                )

                CustomerAccount.objects.create(
                    ssn=customer,
                    account_no=account,
                    last_access_date=timezone.now()
                )

            return redirect('login_view')
        except Exception as e:
            return render(request, 'login.html', {
                'error': f'An error occurred while creating the account: {str(e)}',
                'branches': Branch.objects.all()
            })

    branches = Branch.objects.all()
    return render(request, 'login.html', {'branches': branches})

def get_next_account_no():
    last_account = Account.objects.all().order_by('account_no').last()
    if not last_account:
        return 1000000000
    return last_account.account_no + 1

def get_next_trans_code():
    last_transaction = Transaction.objects.all().order_by('trans_code').last()
    if not last_transaction:
        return 100000
    return last_transaction.trans_code + 1

def customer_dashboard(request, ssn):
    print(f"Loading dashboard for customer SSN: {ssn}")

    customer = get_object_or_404(Customer, ssn=ssn)

    branch_address = customer.branch.address if customer.branch else "No branch assigned"

    associated_employee = customer.e_ssn.name if customer.e_ssn else "No assigned employee"

    customer_accounts = CustomerAccount.objects.filter(ssn=customer.ssn)
    account_details = []
    
    for customer_account in customer_accounts:
        try:
            acc = Account.objects.get(account_no=customer_account.account_no.account_no)
            transactions = Transaction.objects.filter(account_no=acc.account_no)
            
            account_details.append({
                'account_no': acc.account_no,
                'acc_type': acc.acc_type,
                'balance': acc.balance,
                'transactions': transactions
            })
        except Account.DoesNotExist:
            print(f"Account not found for account number: {customer_account.account_no}")

    context = {
        'customer': customer,
        'branch_address': branch_address,
        'associated_employee': associated_employee,
        'accounts': account_details,
    }

    if request.method == 'POST':
        if 'create_account' in request.POST:
            account_type = request.POST.get('account_type')
            if account_type:
                try:
                    with transaction.atomic():
                        account_no = get_next_account_no()
                        
                        new_account = Account.objects.create(
                            account_no=account_no,
                            balance=0.0,
                            branch_id=customer.branch_id,
                            acc_type=account_type
                        )
                        
                        CustomerAccount.objects.create(
                            ssn=customer,
                            account_no=new_account,
                            last_access_date=timezone.now()
                        )
                        
                        return redirect('customer_dashboard', ssn=customer.ssn)
                
                except Exception as e:
                    context['error'] = f'Error creating account: {str(e)}'
                    print(f"Account creation error: {e}")

        elif 'make_transaction' in request.POST:
            account_no = request.POST.get('account_no')
            trans_type = request.POST.get('trans_type')
            amount = request.POST.get('amount')
            chargeable = request.POST.get('chargeable')
            print("Chargeable:", chargeable)

            try:
                amount = Decimal(amount)
                account_no = int(account_no)
                
                with transaction.atomic():
                    account = Account.objects.get(account_no=account_no)
                    
                    trans_code = get_next_trans_code()
                    
                    trans = Transaction.objects.create(
                        trans_code=trans_code,
                        trans_date=timezone.now().date(),
                        hour=timezone.now().hour,
                        trans_type=trans_type,
                        amount=amount,
                        chargeable=chargeable,
                        account_no=account
                    )
                    
                    if trans_type.lower() == 'deposit':
                        account.balance += amount
                    elif trans_type.lower() == 'withdrawal':
                        if account.balance >= amount:
                            account.balance -= amount
                        else:
                            raise ValueError("Insufficient funds")
                    elif trans_type.lower() == 'payment':
                        if account.balance >= amount:
                            account.balance -= amount
                        else:
                            raise ValueError("Insufficient funds")
                    elif trans_type.lower() == 'transfer':
                        if account.balance >= amount:
                            account.balance -= amount
                        else:
                            raise ValueError("Insufficient funds")
                    account.save()
                    
                    return redirect('customer_dashboard', ssn=customer.ssn)
            
            except Exception as e:
                context['error'] = f'Transaction error: {str(e)}'
                print(f"Transaction error: {e}")

    return render(request, 'customer_dashboard.html', context)


def employee_dashboard(request, ssn):
    employee = get_object_or_404(Employee, ssn=ssn)

    branch_name = employee.branch.name if employee.branch else "No branch assigned"

    manager_name = employee.manager_ssn.name if employee.manager_ssn else "No manager assigned"

    customers = Customer.objects.filter(e_ssn=employee)

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

    dependents = Dependent.objects.filter(essn=employee)

    context = {
        'employee': employee,
        'branch_name': branch_name,
        'manager_name': manager_name,
        'customer_details': customer_details,
        'dependents': dependents,
    }

    return render(request, 'employee_dashboard.html', context)

def branch_dashboard(request, branch_id):
    branch = get_object_or_404(Branch, branch_id=branch_id)

    if request.method == 'POST' and 'edit_customer' in request.POST:
        ssn = request.POST.get('ssn')
        customer = get_object_or_404(Customer, ssn=ssn)
        customer.name = request.POST.get('name')
        customer.apt_no = request.POST.get('apt_no')
        customer.street_no = request.POST.get('street_no')
        customer.state = request.POST.get('state')
        customer.city = request.POST.get('city')
        customer.zip = request.POST.get('zip')
        customer.branch_id = request.POST.get('branch_id')
        e_ssn = request.POST.get('e_ssn')
        customer.e_ssn = get_object_or_404(Employee, ssn=e_ssn) if e_ssn else None
        customer.save()

    employees = Employee.objects.filter(branch=branch)

    customer_details = []
    customers = Customer.objects.filter(branch=branch)
    for customer in customers:
        customer_details.append({
            'ssn': customer.ssn,
            'name': customer.name,
            'apt_no': customer.apt_no,
            'street_no': customer.street_no,
            'state': customer.state,
            'city': customer.city,
            'zip': customer.zip,
            'branch': customer.branch,
            'e_ssn': customer.e_ssn,
            'assigned_employee': customer.e_ssn.name if customer.e_ssn else "No assigned employee",
        })

    customer_accounts = Account.objects.filter(branch_id=branch_id)

    context = {
        'branch': branch,
        'employees': employees,
        'customer_details': customer_details,
        'branches': Branch.objects.all(),
        'customer_accounts': customer_accounts,
    }

    return render(request, 'branch_dashboard.html', context)

@csrf_exempt
def edit_customer(request, ssn):
    customer = get_object_or_404(Customer, ssn=ssn)
    if request.method == 'POST':
        customer.name = request.POST.get('name')
        customer.apt_no = request.POST.get('apt_no')
        customer.street_no = request.POST.get('street_no')
        customer.state = request.POST.get('state')
        customer.city = request.POST.get('city')
        customer.zip = request.POST.get('zip')
        customer.branch_id = request.POST.get('branch_id')
        e_ssn = request.POST.get('e_ssn')
        customer.e_ssn = get_object_or_404(Employee, ssn=e_ssn) if e_ssn else None
        customer.save()
        return redirect('branch_dashboard', branch_id=customer.branch_id)
    
    context = {
        'customer': customer,
        'branches': Branch.objects.all(),
        'employees': Employee.objects.all(),
    }
    return render(request, 'edit_customer.html', context)
