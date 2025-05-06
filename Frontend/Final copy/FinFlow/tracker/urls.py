# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Main views
    path('', views.home_view, name='home'),
    path('education/', views.education_view, name='education'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    
  
    # Dashboard and transactions
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add-transaction/', views.add_transaction, name='add_transaction'),
    path('edit_transaction/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    
    # API endpoints
    path('api/transactions/', views.get_transactions, name='api_transactions'),
    path('api/transactions/<int:pk>/delete/', views.delete_transaction, name='api_delete_transaction'),
    path('api/categories/', views.get_categories, name='api_categories'),
    path('api/summary/', views.get_summary, name='api_summary'),
]