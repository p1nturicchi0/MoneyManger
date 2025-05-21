from transactions.models import Transaction, Limit
from datetime import date



def navbar_progress(request):
    if not request.user.is_authenticated:
        return {}

    today = date.today()
    start_month = today.replace(day=1)

    transactions = Transaction.objects.filter(
        user=request.user,
        transaction_date__range=(start_month, today)
    )

    total_expenses = sum(transaction.amount for transaction in transactions if transaction.transaction_type == 'expense')

    limit_obj = Limit.objects.filter(user=request.user).order_by('-created_at').first()
    limit = limit_obj.limit if limit_obj else 0

    procent = int(total_expenses / limit * 100) if limit else 0

    return {
        'total_expenses': total_expenses,
        'limit': limit,
        'procent': procent,
    }