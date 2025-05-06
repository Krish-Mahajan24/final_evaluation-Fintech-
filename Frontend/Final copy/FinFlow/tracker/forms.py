from django import forms
from .api_client import FlaskAPIClient

class TransactionForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    type = forms.ChoiceField(
        choices=[('Income', 'Income'), ('Expense', 'Expense')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    category = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
        choices=[('', '-- Select Category --')]
    )
    description = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fetch categories from Flask API
        client = FlaskAPIClient()
        categories = client.get_items('categories') or []
        print("Fetched categories from Flask:", categories)
        self.fields['category'].choices = [('', '-- Select Category --')] + [
            (cat['id'], cat['name']) for cat in categories
        ]