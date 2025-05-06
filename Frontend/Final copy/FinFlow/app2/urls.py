from django.urls import path
from . import views

urlpatterns = [
    path('', views.goal_list, name='goal_list'),
    path('goals/<int:goal_id>/', views.goal_detail, name='goal_detail'),
    path('goals/create/', views.create_goal, name='create_goal'),
    path('goals/<int:goal_id>/edit/', views.edit_goal, name='edit_goal'),
    path('goals/<int:goal_id>/delete/', views.delete_goal, name='delete_goal'),
    path('goals/<int:goal_id>/milestone/add/', views.add_milestone, name='add_milestone'),
    path('goals/<int:goal_id>/contribution/add/', views.add_contribution, name='add_contribution'),
    path('recommendations/', views.recommendations_view, name='recommendations_view'),
    path('recommendations/', views.generate_recommendations, name='generate_recommendations'),
    path('recommendations/<int:rec_id>/dismiss/', views.dismiss_recommendation, name='dismiss_recommendation'),
]