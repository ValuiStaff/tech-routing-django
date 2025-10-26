from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

def home(request):
    """Home page - shows login or redirect to dashboard"""
    if request.user.is_authenticated:
        if request.user.is_admin():
            return redirect('/admin/')
        elif request.user.is_technician():
            return redirect('core:technician_dashboard')
        elif request.user.is_customer():
            return redirect('core:customer_dashboard')
    
    return render(request, 'home.html')

