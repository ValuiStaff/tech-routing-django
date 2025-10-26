from django.urls import path
from accounts import views
from accounts import technician_signup_views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('technician-signup/', technician_signup_views.technician_signup_view, name='technician_signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]

