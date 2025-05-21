from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from transactions.forms import TransactionForm, TransactionUpdateForm, LimitForm
from transactions.models import Transaction, Limit
from calendar import monthrange
from datetime import date

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

# It is used to
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('transaction_date')

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


class TransactionUpdateView(LoginRequiredMixin,UpdateView):
    template_name = 'transactions/update_transaction.html'
    model = Transaction
    form_class = TransactionUpdateForm
    success_url = '/dashboard/'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class TransactionDeleteView(LoginRequiredMixin,DeleteView):
    template_name = 'transactions/delete_transaction.html'
    model = Transaction
    success_url = '/dashboard/'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

class TransactionDetailView(LoginRequiredMixin,DetailView):
    template_name = 'transactions/transaction_details.html'
    model = Transaction

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class DashboardListView(LoginRequiredMixin,ListView):
    template_name = "transactions/dashboard.html"
    model = Transaction
    context_object_name = "all_transactions"

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('transaction_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_month = self.request.GET.get('month')
        get_year = self.request.GET.get('year')

        if get_month and get_year:
            all_transactions = Transaction.objects.filter(user=self.request.user, transaction_date__month=int(get_month), transaction_date__year=int(get_year)).order_by('transaction_date')
        else:
            all_transactions = {}

        context['all_entries'] = all_transactions
        context['first_page'] = not (get_month and get_year)

        today = date.today()
        monthly_data = []

        for i in range(3):  # ultimele 3 luni
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

            limit_obj = Limit.objects.filter(user=self.request.user).order_by('-created_at').first()
            limit = limit_obj.limit if limit_obj else 0

            procent = int(total_expenses / limit * 100) if limit else 0

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