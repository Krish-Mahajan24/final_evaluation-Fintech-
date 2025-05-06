from django.contrib import admin
from .models import (
    FinancialGoal,
    GoalMilestone,
    GoalContribution,
    SpendingCategory,
    SpendingRecord,
    SavingRecommendation
)

@admin.register(FinancialGoal)
class FinancialGoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'goal_type', 'target_amount', 'current_amount', 'target_date', 'is_completed')
    list_filter = ('goal_type', 'is_completed', 'start_date')
    search_fields = ('name', 'user__username')


@admin.register(GoalMilestone)
class GoalMilestoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'goal', 'amount', 'is_achieved', 'achievement_date')
    list_filter = ('is_achieved',)
    search_fields = ('name', 'goal__name')


@admin.register(GoalContribution)
class GoalContributionAdmin(admin.ModelAdmin):
    list_display = ('goal', 'amount', 'date', 'note')
    list_filter = ('date',)
    search_fields = ('goal__name', 'note')


@admin.register(SpendingCategory)
class SpendingCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(SpendingRecord)
class SpendingRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'date', 'description')
    list_filter = ('category', 'date')
    search_fields = ('user__username', 'description')


@admin.register(SavingRecommendation)
class SavingRecommendationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'potential_savings', 'created_at', 'is_dismissed')
    list_filter = ('is_dismissed', 'created_at')
    search_fields = ('title', 'description', 'user__username')