from transactions.models import Transaction, Limit
from datetime import date



# A progress bar that shows how much of your limit you spent on current month. This is a context processor which is shown on every page!
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

    # Takes all the limits set for current month, then it takes only the last set limit
    limit_obj = Limit.objects.filter(
        user=request.user,
        month=start_month
    ).order_by('-created_at').first()

    limit = limit_obj.limit if limit_obj else 0

    procent = int(total_expenses / limit * 100) if limit else 0

    return {
        'total_expenses': total_expenses,
        'limit': limit,
        'procent': procent,
    }