from django.db import models

class Account(models.Model):
    account_no = models.IntegerField(db_column='Account_No', primary_key=True)  # Field name made lowercase.
    balance = models.DecimalField(db_column='Balance', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    branch = models.ForeignKey('Branch', models.DO_NOTHING, db_column='Branch_id', blank=True, null=True)  # Field name made lowercase.
    acc_type = models.CharField(db_column='Acc_Type', max_length=20, blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'account'


class Branch(models.Model):
    branch_id = models.IntegerField(db_column='Branch_id', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    address = models.CharField(db_column='Address', max_length=100, blank=True, null=True)  # Field name made lowercase.
    assets = models.DecimalField(db_column='Assets', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mgr_ssn = models.ForeignKey(
        'Employee',
        models.DO_NOTHING,
        db_column='Mgr_SSN',
        blank=True,
        null=True,
        related_name='managed_branches',  # Explicit reverse name
    )

    class Meta:
        managed = False
        db_table = 'branch'

class Branch1(models.Model):
    branch_id = models.IntegerField(db_column='Branch_Id', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    address = models.CharField(db_column='Address', max_length=255, blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'branch_1'


class Branch2(models.Model):
    address = models.CharField(db_column='Address', primary_key=True, max_length=255)  # Field name made lowercase.
    assets = models.DecimalField(db_column='Assets', max_digits=15, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    mgr_ssn = models.IntegerField(db_column='Mgr_SSN', blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'branch_2'

class Checking(models.Model):
    account_no = models.OneToOneField(Account, models.DO_NOTHING, db_column='Account_No', primary_key=True)  # Field name made lowercase.
    overdraft = models.DecimalField(db_column='Overdraft', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'checking'

class Cust1(models.Model):
    ssn = models.IntegerField(db_column='SSN', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    branch = models.ForeignKey(Branch1, models.DO_NOTHING, db_column='Branch_Id', blank=True, null=True)  # Field name made lowercase.
    e_ssn = models.ForeignKey('Emp1', models.DO_NOTHING, db_column='E_SSN', blank=True, null=True)  # Field name made lowercase.
    apt_no = models.IntegerField(db_column='Apt_No', blank=True, null=True)  # Field name made lowercase.
    st_no = models.IntegerField(db_column='St_no', blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'cust_1'


class Cust2(models.Model):
    apt_no = models.IntegerField(db_column='Apt_No', primary_key=True)  # Field name made lowercase. The composite primary key (Apt_No, St_no) found, that is not supported. The first column is selected.
    st_no = models.IntegerField(db_column='St_no')  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=30, blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=20, blank=True, null=True)  # Field name made lowercase.
    zip = models.IntegerField(db_column='Zip', blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'cust_2'
        unique_together = (('apt_no', 'st_no'),)


class Customer(models.Model):
    ssn = models.IntegerField(db_column='SSN', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    apt_no = models.IntegerField(db_column='Apt_no', blank=True, null=True)  # Field name made lowercase.
    street_no = models.IntegerField(db_column='Street_no', blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(db_column='State', max_length=20, blank=True, null=True)  # Field name made lowercase.
    city = models.CharField(db_column='City', max_length=30, blank=True, null=True)  # Field name made lowercase.
    zip = models.IntegerField(db_column='Zip', blank=True, null=True)  # Field name made lowercase.
    branch = models.ForeignKey(Branch, models.DO_NOTHING, db_column='Branch_id', blank=True, null=True)  # Field name made lowercase.
    e_ssn = models.ForeignKey(
        'Employee',  # String reference to avoid circular imports
        models.DO_NOTHING,
        db_column='E_SSN',
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = 'customer'


class CustomerAccount(models.Model):
    ssn = models.OneToOneField(Customer, models.DO_NOTHING, db_column='SSN', primary_key=True)  # Field name made lowercase. The composite primary key (SSN, Account_No) found, that is not supported. The first column is selected.
    account_no = models.ForeignKey(Account, models.DO_NOTHING, db_column='Account_No')  # Field name made lowercase.
    last_access_date = models.DateField(db_column='Last_Access_Date', blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'customer_account'
        unique_together = (('ssn', 'account_no'),)


class Dependent(models.Model):
    essn = models.OneToOneField('Employee', models.DO_NOTHING, db_column='ESSN', primary_key=True)  # Field name made lowercase. The composite primary key (ESSN, Name) found, that is not supported. The first column is selected.
    name = models.CharField(db_column='Name', max_length=50)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'dependent'
        unique_together = (('essn', 'name'),)


class Emp1(models.Model):
    ssn = models.IntegerField(db_column='Ssn', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    start_date = models.DateField(db_column='Start_Date', blank=True, null=True)  # Field name made lowercase.
    branch_id = models.IntegerField(db_column='Branch_id', blank=True, null=True)  # Field name made lowercase.
    manager_ssn = models.IntegerField(db_column='Manager_SSN', blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'emp_1'


class Emp2(models.Model):
    ssn = models.IntegerField(db_column='Ssn', primary_key=True)  # Field name made lowercase.
    phone_no = models.CharField(db_column='Phone_no', max_length=20, blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'emp_2'


class Employee(models.Model):
    ssn = models.IntegerField(db_column='SSN', primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    phone_no = models.CharField(db_column='Phone_No', max_length=20, blank=True, null=True)  # Field name made lowercase.
    start_date = models.DateField(db_column='Start_Date', blank=True, null=True)  # Field name made lowercase.
    branch = models.ForeignKey(
        Branch,
        models.DO_NOTHING,
        db_column='Branch_id',
        blank=True,
        null=True,
        related_name='employees',  # Explicit reverse name
    )
    manager_ssn = models.ForeignKey(
        'self',
        models.DO_NOTHING,
        db_column='Manager_SSN',
        blank=True,
        null=True,
    )

    class Meta:
        managed = False
        db_table = 'employee'


class Loan(models.Model):
    account_no = models.OneToOneField(Account, models.DO_NOTHING, db_column='Account_No', primary_key=True)  # Field name made lowercase.
    monthly_repay = models.DecimalField(db_column='Monthly_Repay', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    loan_amt = models.DecimalField(db_column='Loan_Amt', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    fin_int_rate = models.DecimalField(db_column='Fin_Int_Rate', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'loan'

class MoneyMarket(models.Model):
    account_no = models.OneToOneField(Account, models.DO_NOTHING, db_column='Account_No', primary_key=True)  # Field name made lowercase.
    variable_int_rate = models.DecimalField(db_column='Variable_Int_Rate', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'money_market'

class Savings(models.Model):
    account_no = models.OneToOneField(Account, models.DO_NOTHING, db_column='Account_No', primary_key=True)  # Field name made lowercase.
    fixed_int_rate = models.DecimalField(db_column='Fixed_Int_Rate', max_digits=5, decimal_places=2, blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'savings'


class Transaction(models.Model):
    trans_code = models.IntegerField(db_column='Trans_Code', primary_key=True)  # Field name made lowercase.
    trans_date = models.DateField(db_column='Trans_Date', blank=True, null=True)  # Field name made lowercase.
    hour = models.IntegerField(db_column='Hour', blank=True, null=True)  # Field name made lowercase.
    trans_type = models.CharField(db_column='Trans_Type', max_length=20, blank=True, null=True)  # Field name made lowercase.
    amount = models.DecimalField(db_column='Amount', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    chargeable = models.CharField(db_column='Chargeable', max_length=10, blank=True, null=True)  # Field name made lowercase.
    account_no = models.ForeignKey(Account, models.DO_NOTHING, db_column='Account_No', blank=True, null=True)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'transaction'
