from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import TransactionForm
from .api_client import FlaskAPIClient
import datetime

client = FlaskAPIClient()

def dashboard(request):
    """Render the dashboard page"""
    return render(request, 'finance/dashboard.html')

def add_transaction(request):
    """Add a new transaction through Flask API"""
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction_data = {
                'date': form.cleaned_data['date'].isoformat(),
                'type': form.cleaned_data['type'],
                'category': form.cleaned_data['category'],
                'description': form.cleaned_data['description'],
                'amount': float(form.cleaned_data['amount'])
            }
            response = client.create_item('transactions', transaction_data)
            if response:
                return redirect('dashboard')
    else:
        form = TransactionForm()
    
    return render(request, 'add_transaction.html', {'form': form})

def edit_transaction(request, pk):
    """Edit an existing transaction through Flask API"""
    transaction = client.get_item('transactions', pk)
    
    if not transaction:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            update_data = {
                'date': form.cleaned_data['date'].isoformat(),
                'type': form.cleaned_data['type'],
                'category': form.cleaned_data['category'],
                'description': form.cleaned_data['description'],
                'amount': float(form.cleaned_data['amount'])
            }
            response = client.update_item('transactions', pk, update_data)
            if response:
                return redirect('dashboard')
    else:
        initial_data = {
            'date': datetime.date.fromisoformat(transaction['date']),
            'type': transaction['type'],
            'category': transaction['category'],
            'description': transaction['description'],
            'amount': transaction['amount']
        }
        form = TransactionForm(initial=initial_data)
    
    return render(request, 'edit_transaction.html', {
        'form': form,
        'transaction': transaction
    })

def get_transactions(request):
    """API endpoint to get transactions with optional filtering"""
    filters = {
        'month': request.GET.get('month'),
        'year': request.GET.get('year'),
        'category': request.GET.get('category')
    }
    transactions = client.get_items('transactions', params=filters) or []
    return JsonResponse(transactions, safe=False)

def get_categories(request):
    """API endpoint to get all categories"""
    categories = client.get_items('categories') or []
    return JsonResponse(categories, safe=False)

def delete_transaction(request, pk):
    """API endpoint to delete a transaction"""
    if request.method == 'DELETE':
        success = client.delete_item('transactions', pk)
        return JsonResponse({'status': 'success' if success else 'error'})
    return JsonResponse({'status': 'error'}, status=405)

def get_summary(request):
    """API endpoint to get summary statistics"""
    summary = client.get_items('summary') or {
        'total_income': 0,
        'total_expenses': 0,
        'total_balance': 0,
        'monthly_trend': [],
        'category_breakdown': []
    }
    return JsonResponse(summary)

def home_view(request):
    return render(request, 'index.html')

def education_view(request):
    return render(request, 'education.html')

def about_view(request):
    return render(request, 'about.html')

def dashboard_view(request):
    return render(request, 'dashboard.html')

def contact_view(request):
    return render(request, 'contact.html')