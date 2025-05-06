# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.views import LoginView
from .forms import SignUpForm, CustomLoginForm
from .models import User

class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        role = form.cleaned_data.get('role')
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Check if requesting admin role
            if role == 'admin' and not user.is_staff:
                form.add_error(None, "You don't have administrator privileges.")
                return self.form_invalid(form)
                
            # Set role if appropriate
            if role and user.is_staff:
                user.role = role
                user.save()
                
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)
            
def dashboard(request):
    """Render the dashboard page for logged-in users."""
    return render(request, 'accounts/dashboard.html')


from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('home')  # Replace 'home' with your homepage URL name