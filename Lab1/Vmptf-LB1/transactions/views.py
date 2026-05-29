from django.shortcuts import render, redirect
from .models import Transaction, Category
from .forms import TransactionForm

def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-id')
    categories = Category.objects.all()
    return render(request, 'transactions/list.html', {
        'transactions': transactions,
        'categories': categories
    })

def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'transactions/add.html', {'form': form})

def transactions_by_category(request, category_id):
    category = Category.objects.get(id=category_id)
    transactions = category.transactions.all()
    return render(request, 'transactions/by_category.html', {
        'category': category,
        'transactions': transactions
    })