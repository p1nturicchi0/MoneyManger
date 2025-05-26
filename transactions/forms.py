from django import forms
from datetime import datetime, date
from transactions.models import Transaction, Limit


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ['total', 'user']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name of expense'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control',  'placeholder': 'Amount'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'transaction_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

# A validation form so the user can`t have unreasonable data
    def clean(self):
        cleaned_data = self.cleaned_data

# The amount can`t be negative

        all_amounts = Transaction.objects.all()
        for transaction in all_amounts:
            if transaction.amount < 0:
                msg = "Amount can not be negative!"
                self.add_error('amount', msg)

# The transaction can`t be a future transaction

        get_transaction_date = cleaned_data.get('transaction_date')
        now = datetime.now().date()
        if get_transaction_date > now:
            msg = "The date of transaction can not be in the future!"
            self.add_error('transaction_date', msg)

        return cleaned_data

class TransactionUpdateForm(forms.ModelForm):
    class Meta:
        model = Transaction
        exclude = ['name', 'transaction_date', 'user']

        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
        }

class LimitForm(forms.ModelForm):
    month = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'month'}),
        input_formats=['%Y-%m'],
    )

    class Meta:
        model = Limit
        exclude = ['total', 'user']

        widgets = {

            'limit': forms.NumberInput(attrs={'class': 'form-control',  'placeholder': 'Max desired limit'}),
            'month': forms.DateInput(attrs={'class': 'form-control', 'type': 'month'}),

        }

# Limit can`t be negative

    def clean_limit(self):
        limit = self.cleaned_data.get('limit')
        if limit < 0:
            msg = 'Max limit can not be negative!'
            self.add_error('limit', msg)
        return limit