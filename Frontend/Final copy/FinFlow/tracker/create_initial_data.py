from django.db import transaction
from tracker.models import Category

def create_initial_categories():
    # Only run if no categories exist
    if Category.objects.exists():
        return "Categories already exist!"
    
    with transaction.atomic():
        # Common income categories
        Category.objects.create(name="Salary", transaction_type="Income")
        Category.objects.create(name="Bonus", transaction_type="Income")
        Category.objects.create(name="Investment", transaction_type="Income")
        Category.objects.create(name="Gift", transaction_type="Income")
        Category.objects.create(name="Other Income", transaction_type="Income")

        # Common expense categories
        Category.objects.create(name="Housing", transaction_type="Expense")
        Category.objects.create(name="Food", transaction_type="Expense")
        Category.objects.create(name="Transportation", transaction_type="Expense")
        Category.objects.create(name="Utilities", transaction_type="Expense")
        Category.objects.create(name="Entertainment", transaction_type="Expense")
        Category.objects.create(name="Healthcare", transaction_type="Expense")
        Category.objects.create(name="Education", transaction_type="Expense")
        Category.objects.create(name="Shopping", transaction_type="Expense")
        Category.objects.create(name="Other Expense", transaction_type="Expense")
    
    return "Initial categories created successfully!"