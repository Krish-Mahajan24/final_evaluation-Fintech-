from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Avg
from decimal import Decimal

from .models import (
    FinancialGoal, 
    GoalMilestone, 
    GoalContribution, 
    SpendingRecord,
    SavingRecommendation
)
from .forms import FinancialGoalForm, GoalMilestoneForm, GoalContributionForm


@login_required
def goal_list(request):
    goals = FinancialGoal.objects.filter(user=request.user)
    
    # Calculate stats for goals
    total_saved = sum(goal.current_amount for goal in goals)
    total_target = sum(goal.target_amount for goal in goals)
    
    # Calculate overall progress
    overall_progress = 0
    if total_target > 0:
        overall_progress = int((total_saved / total_target) * 100)
    
    # Get recent contributions
    recent_contributions = GoalContribution.objects.filter(
        goal__user=request.user
    ).order_by('-date')[:5]
    
    context = {
        'goals': goals,
        'total_saved': total_saved,
        'total_target': total_target,
        'overall_progress': overall_progress,
        'recent_contributions': recent_contributions,
    }
    return render(request, 'goal_list.html', context)

@login_required
def goal_detail(request, goal_id):
    goal = get_object_or_404(FinancialGoal, id=goal_id, user=request.user)
    milestones = goal.milestones.all().order_by('amount')
    contributions = goal.contributions.all().order_by('-date')
    
    # Calculate days remaining
    days_remaining = (goal.target_date - timezone.now().date()).days
    
    # Calculate required monthly contribution to reach goal on time
    required_monthly = Decimal('0.00')
    if days_remaining > 0:
        remaining_amount = goal.target_amount - goal.current_amount
        months_remaining = days_remaining / 30.0  # approximate
        if months_remaining > 0:
            required_monthly = remaining_amount / Decimal(months_remaining)
    
    context = {
        'goal': goal,
        'milestones': milestones,
        'contributions': contributions,
        'days_remaining': days_remaining,
        'required_monthly': required_monthly,
        'progress_percentage': goal.get_progress_percentage(),
        'is_on_track': goal.is_on_track(),
    }
    return render(request, 'goal_detail.html', context)

@login_required
def create_goal(request):
    if request.method == 'POST':
        form = FinancialGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            
            # Auto-create milestones at 25%, 50%, and 75%
            milestone_percentages = [25, 50, 75]
            for percentage in milestone_percentages:
                amount = (goal.target_amount * percentage) / 100
                milestone = GoalMilestone(
                    goal=goal,
                    name=f"{percentage}% Progress",
                    amount=amount
                )
                milestone.save()
                
            messages.success(request, f"Financial goal '{goal.name}' created successfully!")
            return redirect('goal_detail', goal_id=goal.id)
    else:
        form = FinancialGoalForm()
    
    return render(request, 'create_goal.html', {'form': form})

@login_required
def edit_goal(request, goal_id):
    goal = get_object_or_404(FinancialGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        form = FinancialGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, f"Goal '{goal.name}' updated successfully!")
            return redirect('goal_detail', goal_id=goal.id)
    else:
        form = FinancialGoalForm(instance=goal)
    
    return render(request, 'edit_goal.html', {'form': form, 'goal': goal})


def delete_goal(request, goal_id):
    """
    View function to handle deleting a financial goal.
    """
    # Get the goal object or return 404 if not found
    goal = get_object_or_404(FinancialGoal, id=goal_id)
    
    if request.method == 'POST':
        goal_title = goal.name
        
        goal.delete()
        
        messages.success(request, f'Goal "{goal_title}" has been successfully deleted.')
        
        return redirect('goal_list')  
    
    return render(request, 'delete_goal.html', {'goal': goal})


@login_required
def add_milestone(request, goal_id):
    goal = get_object_or_404(FinancialGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        form = GoalMilestoneForm(goal, request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.goal = goal
            milestone.save()
            messages.success(request, f"Milestone '{milestone.name}' added successfully!")
            return redirect('goal_detail', goal_id=goal.id)
    else:
        form = GoalMilestoneForm(goal)
    
    return render(request, 'add_milestone.html', {
        'form': form, 
        'goal': goal
    })

@login_required
def add_contribution(request, goal_id):
    goal = get_object_or_404(FinancialGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        form = GoalContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.goal = goal
            contribution.save()
            
            # Check if goal is completed
            if goal.current_amount >= goal.target_amount:
                goal.is_completed = True
                goal.save()
                messages.success(request, f"Congratulations! You've reached your goal: '{goal.name}'!")
            else:
                messages.success(request, f"Contribution of ${contribution.amount} added successfully!")
            
            return redirect('goal_detail', goal_id=goal.id)
    else:
        form = GoalContributionForm(initial={'date': timezone.now().date()})
    
    return render(request, 'add_contribution.html', {
        'form': form, 
        'goal': goal
    })

@login_required
def recommendations_view(request):
    """
    View function to display recommendations to the user.
    This function reuses the generated recommendations or creates new ones if needed.
    """
    user = request.user
    
    # Get all active recommendations
    active_recommendations = SavingRecommendation.objects.filter(
        user=user,
        is_dismissed=False
    ).order_by('-created_at')
    
    # If there are no active recommendations, generate new ones
    if not active_recommendations.exists():
        # Generate new recommendations
        generate_recommendations(request)
        # Refresh the recommendations list
        active_recommendations = SavingRecommendation.objects.filter(
            user=user,
            is_dismissed=False
        ).order_by('-created_at')
    
    return render(request, 'recommendations.html', {
        'recommendations': active_recommendations
    })

@login_required
def generate_recommendations(request):
    user = request.user
    # Get spending patterns for the last 3 months
    three_months_ago = timezone.now().date().replace(day=1)
    three_months_ago = three_months_ago.replace(month=three_months_ago.month - 3 if three_months_ago.month > 3 else three_months_ago.month + 9)
    spending_data = SpendingRecord.objects.filter(
        user=user,
        date__gte=three_months_ago
    ).values('category__name').annotate(
        total_spent=Sum('amount'),
        avg_per_day=Avg('amount')
    ).order_by('-total_spent')
    
    # Create recommendations based on spending patterns
    recommendations = []
    
    # Find categories with high spending
    if spending_data:
        top_category = spending_data[0]
        recommendations.append({
            'title': f"Reduce spending on {top_category['category__name']}",
            'description': f"You've spent ${top_category['total_spent']} on {top_category['category__name']} in the last 3 months. Consider reducing this by 15% to save ${top_category['total_spent'] * 0.15:.2f}.",
            'potential_savings': top_category['total_spent'] * Decimal('0.15')
        })
    
    # Look for recurring small expenses
    small_expenses = SpendingRecord.objects.filter(
        user=user,
        date__gte=three_months_ago,
        amount__lt=20
    ).count()
    
    if small_expenses > 10:
        recommendations.append({
            'title': "Cut back on small purchases",
            'description': f"You've made {small_expenses} small purchases under $20 in the last 3 months. These add up! Try reducing these by half.",
            'potential_savings': Decimal('10.00') * small_expenses / 2  # Rough estimate
        })
    
    # Save recommendations to database
    for rec in recommendations:
        SavingRecommendation.objects.create(
            user=user,
            title=rec['title'],
            description=rec['description'],
            potential_savings=rec['potential_savings']
        )
    
    # Get all active recommendations
    active_recommendations = SavingRecommendation.objects.filter(
        user=user,
        is_dismissed=False
    ).order_by('-created_at')
    
    return render(request, 'recommendations.html', {
        'recommendations': active_recommendations
    })

@login_required
def dismiss_recommendation(request, rec_id):
    recommendation = get_object_or_404(SavingRecommendation, id=rec_id, user=request.user)
    recommendation.is_dismissed = True
    recommendation.save()
    messages.success(request, "Recommendation dismissed.")
    return redirect('recommendations_view')