from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView, TemplateView
from transactions.forms import TransactionForm, TransactionUpdateForm, LimitForm
from transactions.models import Transaction, Limit
from calendar import monthrange
from datetime import date
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.timezone import now
from django.views import View
from django.template.loader import render_to_string


# We use the form from our form.py file in order to create a transaction in our database
# LoginRequiredMixin is used for the users to be logged in order to view certain pages from the application
class TransactionCreateView(LoginRequiredMixin,CreateView):
    template_name = 'transactions/create_transaction.html'
    model = Transaction
    form_class = TransactionForm
    success_url = '/dashboard/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TransactionListView(LoginRequiredMixin,ListView):
    template_name = "transactions/transactions_list.html"
    model = Transaction
    context_object_name = "all_transactions"

# It is used get the information stored by a username using it`s primary key which is unique
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-transaction_date')

# We make a total using the amounts that the user inputs, if they are income they will be added and if they are expenses they will be substracted
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total = 0
        all_entries = self.get_queryset()

        for entry in all_entries:
            if entry.transaction_type == 'income':
                total += entry.amount
            else:
                total -= entry.amount

        transactions = Transaction.objects.filter(user=self.request.user).order_by('transaction_date')
        first_transaction = transactions.first()
        last_transaction = transactions.last()

        context['first_transaction_date'] = first_transaction.transaction_date if first_transaction else None
        context['last_transaction_date'] = last_transaction.transaction_date if last_transaction else None

        context['total'] = total


        return context

# This is a form where users can update their transactions
class TransactionUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'transactions/update_transaction.html'
    model = Transaction
    form_class = TransactionUpdateForm
    success_url = '/dashboard/'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

# The user can delete a transactions of his choice
class TransactionDeleteView(LoginRequiredMixin,DeleteView):
    template_name = 'transactions/delete_transaction.html'
    model = Transaction
    success_url = '/dashboard/'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

# The user can see details of his transaction
class TransactionDetailView(LoginRequiredMixin,DetailView):
    template_name = 'transactions/transaction_details.html'
    model = Transaction

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

 # The dashboard page where the user has information about his transactions and can make multiple actions
class DashboardListView(LoginRequiredMixin,ListView):
    template_name = "transactions/dashboard.html"
    model = Transaction
    context_object_name = "all_transactions"

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('transaction_date')

# The user can choose which month to be shown on his dashboard
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_month = self.request.GET.get('month')
        get_year = self.request.GET.get('year')

# Filter the transactions by month and year
        if get_month and get_year:
            all_transactions = Transaction.objects.filter(user=self.request.user, transaction_date__month=int(get_month), transaction_date__year=int(get_year)).order_by('transaction_date')
        else:
            all_transactions = {}

        context['all_entries'] = all_transactions
        context['first_page'] = not (get_month and get_year)

        today = date.today()
        monthly_data = []

# A report for last 3 months when the user has a status based on hid expenditure
        for i in range(3):
            year, month = self.get_previous_month(today.year, today.month, i)
            start_date = date(year, month, 1)
            last_day = monthrange(year, month)[1]
            end_date = date(year, month, last_day)

            transactions = Transaction.objects.filter(
                user=self.request.user,
                transaction_date__range=(start_date, end_date)
            )

            total_expenses = sum(
                transaction.amount for transaction in transactions if transaction.transaction_type == 'expense'
            )

            limit_obj = Limit.objects.filter(
                user=self.request.user,
                month=start_date
            ).order_by('-created_at').first()

            limit = limit_obj.limit if limit_obj else 0

            procent = int(total_expenses / limit * 100) if limit else 0

# User status based on expenditure

            if procent < 50:
                status = 'Moderate spender'
            elif procent < 80:
                status = 'Big spender'
            elif procent < 100:
                status = 'At risk'
            else:
                status = 'Over the budget'

            monthly_data.append({
                'month': start_date.strftime('%B %Y'),
                'total_expenses': total_expenses,
                'limit': limit,
                'procent': procent,
                'status': status,
            })

        context['monthly_data'] = monthly_data

        return context

    def get_previous_month(self, year, month, minus):
        month -= minus
        while month <= 0:
            month += 12
            year -= 1
        return year, month

# A form where the user can set a Budget Limit for a month of his choice
class LimitCreateView(LoginRequiredMixin,CreateView):
    template_name = 'transactions/transactions_limit.html'
    model = Limit
    form_class = LimitForm
    success_url = '/dashboard/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

# User`s profile where he can see his details
class ProfileListView(LoginRequiredMixin,ListView):
    model = User
    template_name = 'transactions/profile.html'
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        transactions = Transaction.objects.filter(user=self.request.user).order_by('transaction_date')
        first = transactions.first()
        last = transactions.last()

        context['first_transaction_date'] = first.transaction_date if first else None
        context['last_transaction_date'] = last.transaction_date if last else None

        return context

# An email report of previous month that users can receive on their email
class SendMonthlyReportView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = self.request.user
        today = now().date()

        # Picking last month for report
        last_month_year, last_month = self.get_previous_month(today.year, today.month, 1)
        start_date = date(last_month_year, last_month, 1)
        end_day = monthrange(last_month_year, last_month)[1]
        end_date = date(last_month_year, last_month, end_day)

        transactions = Transaction.objects.filter(
            user=user,
            transaction_date__range=(start_date, end_date)
        )

        total_expenses = sum(
            transaction.amount for transaction in transactions if transaction.transaction_type == 'expense'
        )

        limit_obj = Limit.objects.filter(
            user=user,
            month=start_date
        ).order_by('-created_at').first()

        limit = limit_obj.limit if limit_obj else 0
        procent = int(total_expenses / limit * 100) if limit else 0

        # Email content
        subject = f"Monthly report - {start_date.strftime('%B %Y')}"
        message = render_to_string('transactions/email_report.html', {
            'user': user,
            'transactions': transactions,
            'limit': limit,
            'total_expenses': total_expenses,
            'procent': procent,
            'month_name': start_date.strftime('%B %Y'),
        })

        # Sending email
        send_mail(
            subject,
            message,
            'django@dvpconstruct.ro',
            [user.email],
            fail_silently=False,
        )

        messages.success(request, f"{start_date.strftime('%B %Y')} report was sent on {user.email}")
        return redirect('dashboard')

    def get_previous_month(self, year, month, minus):
        month -= minus
        while month <= 0:
            month += 12
            year -= 1
        return year, month