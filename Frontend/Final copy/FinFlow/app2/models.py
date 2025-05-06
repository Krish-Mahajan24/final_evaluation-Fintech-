from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class FinancialGoal(models.Model):
    GOAL_TYPES = [
        ('VAC', 'Vacation'),
        ('EMF', 'Emergency Fund'),
        ('HDP', 'House Down Payment'),
        ('CAR', 'Vehicle'),
        ('EDU', 'Education'),
        ('RET', 'Retirement'),
        ('DEB', 'Debt Payoff'),
        ('OTH', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='financial_goals')
    name = models.CharField(max_length=100)
    goal_type = models.CharField(max_length=3, choices=GOAL_TYPES)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateField(default=timezone.now)
    target_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.get_goal_type_display()}"
    
    def get_progress_percentage(self):
        if self.target_amount == 0:
            return 0
        return int((self.current_amount / self.target_amount) * 100)
    
    def is_on_track(self):
        if self.target_date < timezone.now().date():
            return False

        # Calculate the expected progress based on time elapsed
        total_days = (self.target_date - self.start_date).days
        days_passed = (timezone.now().date() - self.start_date).days

        if total_days <= 0:
            return False

        # Convert to Decimal for compatibility
        progress_ratio = Decimal(days_passed) / Decimal(total_days)
        expected_progress = progress_ratio * self.target_amount

        return self.current_amount >= expected_progress


class GoalMilestone(models.Model):
    goal = models.ForeignKey(FinancialGoal, on_delete=models.CASCADE, related_name='milestones')
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(blank=True, null=True)
    is_achieved = models.BooleanField(default=False)
    achievement_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.amount}"
    
    class Meta:
        ordering = ['amount']


class GoalContribution(models.Model):
    goal = models.ForeignKey(FinancialGoal, on_delete=models.CASCADE, related_name='contributions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    note = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return f"{self.goal.name} - ${self.amount} on {self.date}"
    
    class Meta:
        ordering = ['-date']
    
    def save(self, *args, **kwargs):
        # Update the goal's current amount when a contribution is made
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.goal.current_amount += self.amount
            self.goal.save()
            
            # Check if any milestones have been achieved
            for milestone in self.goal.milestones.filter(is_achieved=False):
                if self.goal.current_amount >= milestone.amount:
                    milestone.is_achieved = True
                    milestone.achievement_date = timezone.now().date()
                    milestone.save()


class SpendingCategory(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Spending Categories"


class SpendingRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='spending_records')
    category = models.ForeignKey(SpendingCategory, on_delete=models.SET_NULL, null=True, related_name='records')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=200, blank=True, null=True)
    
    def __str__(self):
        return f"{self.category.name} - ${self.amount} on {self.date}"
    
    class Meta:
        ordering = ['-date']


class SavingRecommendation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saving_recommendations')
    title = models.CharField(max_length=100)
    description = models.TextField()
    potential_savings = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_dismissed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title