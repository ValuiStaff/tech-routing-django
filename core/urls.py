from django.urls import path
from core import views
from core import customer_views
from core import technician_views
from core.admin import bulk_upload_view

app_name = 'core'

urlpatterns = [
    # Admin views
    path('admin/assign/', views.admin_assign_view, name='admin_assign'),
    path('admin/map/', views.admin_map_view, name='admin_map'),
    path('admin/technician/', views.admin_technician_view, name='admin_technician'),
    path('admin/technician/<int:technician_id>/', views.admin_technician_view, name='admin_technician_detail'),
    path('admin/bulk-upload/', bulk_upload_view, name='bulk_upload'),
    
    # Customer views
    path('customer/dashboard/', customer_views.customer_dashboard, name='customer_dashboard'),
    path('customer/submit/', customer_views.customer_submit_request, name='customer_submit'),
    path('customer/nearby/', customer_views.customer_nearby_technicians, name='customer_nearby'),
    
    # Technician views
    path('technician/dashboard/', technician_views.technician_dashboard, name='technician_dashboard'),
    path('technician/map/', technician_views.technician_route_map, name='technician_map'),
    path('technician/profile/', technician_views.technician_profile, name='technician_profile'),
    path('technician/signup/', technician_views.technician_signup, name='technician_signup'),
    path('technician/update-status/<int:assignment_id>/', technician_views.technician_update_status, name='technician_update_status'),
]

