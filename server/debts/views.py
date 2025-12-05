from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Debt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.db.models import Sum
from decimal import Decimal
from django.db import connection

@login_required
def homePage(request):
    user = request.user
    debts_owed = Debt.objects.filter(debtor=user)
    debts_lent = Debt.objects.filter(creditor=user)

    total_debt = debts_owed.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_credit = debts_lent.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    balance = total_credit - total_debt
    abs_balance = abs(balance)

    users = User.objects.exclude(pk=user.pk)

    context = {
        'user': user,
        'debts_owed': debts_owed,
        'debts_lent': debts_lent,
        'balance': balance,
        'abs_balance': abs_balance,
        'users': users,
    }

    return render(request, 'index.html', context)

@login_required
def addDebt(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        target_id = request.POST.get('target')
        amount = request.POST.get('amount')
        description = request.POST.get('description', '')
        target = User.objects.get(pk=target_id)

        if role == 'creditor':
            creditor = request.user
            debtor = target
        else:
            creditor = target
            debtor = request.user

        if Debt.objects.filter(
            Q(debtor=debtor, creditor=creditor) |
            Q(debtor=creditor, creditor=debtor)
        ).exists():
            user = request.user
            debts_owed = Debt.objects.filter(debtor=user)
            debts_lent = Debt.objects.filter(creditor=user)
            total_debt = debts_owed.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            total_credit = debts_lent.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            balance = total_credit - total_debt
            abs_balance = abs(balance)
            users = User.objects.exclude(pk=user.pk)

            return render(request, 'index.html', {
                'error': 'Debt already exists between these users.',
                'user': user,
                'debts_owed': debts_owed,
                'debts_lent': debts_lent,
                'balance': balance,
                'abs_balance': abs_balance,
                'users': users,
            })

        # FLAW 2: Injection
        # FLAW: SQL Injection vulnerability
        # User-supplied values are concatenated directly
        # into an SQL query without parameterization.
        # Example payload: ' OR 1=1 --
        cursor = connection.cursor()
        cursor.execute(
            f"INSERT INTO debts_debt (debtor_id, creditor_id, amount, description) "
            f"VALUES ({debtor.id}, {creditor.id}, {amount}, '{description}')"
        )

        """
        # FIX: Use parameterized SQL queries
        cursor = connection.cursor()
        cursor.execute(
            #"INSERT INTO debts_debt (amount, description, creditor_id, debtor_id) VALUES (%s, %s, %s, %s)",
            #[amount, description, creditor.id, debtor.id]
        )
        """
        return redirect('/')

    return redirect('/')

@login_required
@csrf_exempt # FLAW 4: Disabling CSRF protection for this view.
# This exposes the application to CSRF attacks.
def deleteDebt(request, debt_id):
    """
    # FIX: Remove @csrf_exempt decorator to enable Django's built-in CSRF protection.
    """
    try:
        debt = Debt.objects.get(pk=debt_id)
    except Debt.DoesNotExist:
        return redirect('/')

    # FLAW 1: Broken Access Control
    # Flaw: Missing proper permission check,
    # both debtor and creditor can delete the debt.
    # This should be restricted so only creditor can delete.

    if request.method == 'POST':
        debt.delete()
        return redirect('/')

    """
    FIX: Restrict deletion to creditor only:

    if request.method == 'POST':
        if request.user != debt.creditor:
            user = request.user
            debts_owed = Debt.objects.filter(debtor=user)
            debts_lent = Debt.objects.filter(creditor=user)
            total_debt = debts_owed.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            total_credit = debts_lent.aggregate(total=Sum('amount'))['total'] or Decimal('0')
            balance = total_credit - total_debt
            abs_balance = abs(balance)
            users = User.objects.exclude(pk=user.pk)

            return render(request, 'index.html', {
                'error': 'Only creditor can settle the debt.',
                'user': user,
                'debts_owed': debts_owed,
                'debts_lent': debts_lent,
                'balance': balance,
                'abs_balance': abs_balance,
                'users': users,
            })

        debt.delete()
        return redirect('/')
    """