from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.forms import UserLoginForm, CustomerRegistrationForm


def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            # Redirect based on role
            if user.is_admin():
                return redirect('/admin/')
            elif user.is_technician():
                return redirect('core:technician_dashboard')
            elif user.is_customer():
                return redirect('core:customer_dashboard')
            return redirect('/admin/')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


def register_view(request):
    """Customer registration"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.role = 'CUSTOMER'  # Set role to CUSTOMER
            user.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            return redirect('core:customer_dashboard')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard_view(request):
    """Role-based dashboard redirect"""
    user = request.user
    
    if user.is_customer():
        return redirect('core:customer_dashboard')
    elif user.is_technician():
        return redirect('core:technician_dashboard')
    elif user.is_admin():
        return redirect('/admin/')
    else:
        messages.error(request, 'Invalid user role.')
        logout(request)
        return redirect('accounts:login')
