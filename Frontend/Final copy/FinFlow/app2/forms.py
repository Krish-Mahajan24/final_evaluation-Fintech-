from django import forms
from .models import FinancialGoal, GoalMilestone, GoalContribution
from datetime import date


class FinancialGoalForm(forms.ModelForm):
    class Meta:
        model = FinancialGoal
        fields = ['name', 'goal_type', 'target_amount', 'target_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_target_date(self):
        target_date = self.cleaned_data.get('target_date')
        if target_date and target_date < date.today():
            raise forms.ValidationError("Target date cannot be in the past.")
        return target_date
    
    def clean_target_amount(self):
        target_amount = self.cleaned_data.get('target_amount')
        if target_amount <= 0:
            raise forms.ValidationError("Target amount must be greater than zero.")
        return target_amount


class GoalMilestoneForm(forms.ModelForm):
    class Meta:
        model = GoalMilestone
        fields = ['name', 'amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, goal=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.goal = goal
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Milestone amount must be greater than zero.")
        
        if self.goal and amount >= self.goal.target_amount:
            raise forms.ValidationError("Milestone amount should be less than the goal's target amount.")
        
        return amount


class GoalContributionForm(forms.ModelForm):
    class Meta:
        model = GoalContribution
        fields = ['amount', 'date', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Contribution amount must be greater than zero.")
        return amount