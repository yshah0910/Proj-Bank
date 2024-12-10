from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse  # Ensure reverse is imported
from bank.bankk.models import Customer, Employee, Branch, Transaction, Dependent, CustomerAccount, Loan, Savings, Checking, Account
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.db import transaction
import random
from django.utils import timezone
from decimal import Decimal  # Ensure Decimal is imported



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
                next_account_no = get_next_account_no()

                # Create the Account record
                account = Account.objects.create(
                    account_no=next_account_no,
                    balance=0.0,  # Default initial balance
                    branch_id=branch_id,
                    acc_type=account_type
                )

                # Create the CustomerAccount record
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

    # Render the signup form with available branches
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

    # Fetch customer details
    customer = get_object_or_404(Customer, ssn=ssn)

    branch_address = customer.branch.address if customer.branch else "No branch assigned"
    associated_employee = customer.e_ssn.name if customer.e_ssn else "No assigned employee"

    customer_accounts = CustomerAccount.objects.filter(ssn=customer.ssn)
    account_details = []
    
    for customer_account in customer_accounts:
        try:
            # Correctly fetch the Account object using the account_no
            acc = Account.objects.get(account_no=customer_account.account_no.account_no)
            # Fetch transactions for this account
            transactions = Transaction.objects.filter(account_no=acc.account_no)
            
            account_details.append({
                'account_no': acc.account_no,
                'acc_type': acc.acc_type,
                'balance': acc.balance,
                'transactions': transactions
            })
        except Account.DoesNotExist:
            print(f"Account not found for account number: {customer_account.account_no}")

    all_accounts = Account.objects.exclude(account_no__in=[account['account_no'] for account in account_details])

    context = {
        'customer': customer,
        'branch_address': branch_address,
        'associated_employee': associated_employee,
        'accounts': account_details,
        'all_accounts': all_accounts,
    }

    if request.method == 'POST':
        if 'create_account' in request.POST:
            account_type = request.POST.get('account_type')
            if account_type:
                try:
                    with transaction.atomic():
                        # Generate next account number
                        account_no = get_next_account_no()
                        
                        # Create new Account
                        new_account = Account.objects.create(
                            account_no=account_no,
                            balance=0.0,
                            branch_id=customer.branch_id,
                            acc_type=account_type
                        )
                        
                        # Create CustomerAccount linking
                        CustomerAccount.objects.create(
                            ssn=customer,
                            account_no=new_account,  # Pass the Account instance
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
            to_account_type = request.POST.get('to_account_type')  # Identify transfer type
            to_account_no_self = request.POST.get('to_account_no_self')  # For own accounts
            to_account_no_other = request.POST.get('to_account_no_other')  # For other accounts

            try:
                amount = Decimal(amount)
                account_no = int(account_no)

                with transaction.atomic():
                    # Fetch the source account
                    account = Account.objects.get(account_no=account_no)

                    if trans_type.lower() == 'transfer':
                        # Determine target account
                        if to_account_type == 'self':
                            if not to_account_no_self:
                                raise ValueError("Target account must be selected for transfers to your own accounts.")
                            target_account_no = int(to_account_no_self)
                        elif to_account_type == 'other':
                            if not to_account_no_other:
                                raise ValueError("Target account number must be provided for transfers to another customer.")
                            target_account_no = int(to_account_no_other)
                        else:
                            raise ValueError("Invalid transfer type selected.")

                        # Fetch target account
                        target_account = Account.objects.get(account_no=target_account_no)

                        # Ensure sufficient balance
                        if account.balance < amount:
                            raise ValueError("Insufficient funds for transfer.")

                        # Deduct from source account
                        account.balance -= amount
                        account.save()

                        # Add to target account
                        target_account.balance += amount
                        target_account.save()

                        # Log transactions for both accounts
                        trans_code = get_next_trans_code()
                        Transaction.objects.create(
                            trans_code=trans_code,
                            trans_date=timezone.now().date(),
                            hour=timezone.now().hour,
                            trans_type='Transfer Out',
                            amount=amount,
                            chargeable=chargeable,
                            account_no=account,
                        )

                        trans_code = get_next_trans_code()
                        Transaction.objects.create(
                            trans_code=trans_code,
                            trans_date=timezone.now().date(),
                            hour=timezone.now().hour,
                            trans_type='Transfer In',
                            amount=amount,
                            chargeable=chargeable,
                            account_no=target_account,
                        )
                    else:
                        # Handle other transaction types
                        trans_code = get_next_trans_code()
                        trans = Transaction.objects.create(
                            trans_code=trans_code,
                            trans_date=timezone.now().date(),
                            hour=timezone.now().hour,
                            trans_type=trans_type,
                            amount=amount,
                            chargeable=chargeable,
                            account_no=account,
                        )
                        if trans_type.lower() == 'deposit':
                            account.balance += amount
                        elif trans_type.lower() in ['withdrawal', 'payment']:
                            if account.balance < amount:
                                raise ValueError("Insufficient funds.")
                            account.balance -= amount
                        account.save()

                    return redirect('customer_dashboard', ssn=customer.ssn)

            except Exception as e:
                context['error'] = f'Transaction error: {str(e)}'
                print(f"Transaction error: {e}")


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
