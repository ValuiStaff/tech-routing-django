from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.admin import ModelAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from core.models import Skill, Technician, ServiceRequest, Assignment, GoogleMapsConfig
from routing.services import RoutingService


class AssignmentAdminViews:
    """Custom admin views for assignment functionality"""
    
    @staticmethod
    def admin_assign_view(request):
        """Admin assignment interface - trigger OR-Tools matching"""
        # Simple check - if user is staff, they can access
        if not request.user.is_staff:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        
        config = GoogleMapsConfig.load()
        
        if request.method == 'POST':
            # Get selected date
            assigned_date_str = request.POST.get('assigned_date', '')
            if not assigned_date_str:
                messages.error(request, 'Please select a date.')
            else:
                # Parse date
                from datetime import datetime
                assigned_date = datetime.strptime(assigned_date_str, '%Y-%m-%d').date()
                
                # Get pending service requests
                pending_requests = ServiceRequest.objects.filter(
                    status='pending',
                    lat__isnull=False,
                    lon__isnull=False
                )
                
                # Get active technicians with valid coordinates
                active_technicians = Technician.objects.filter(
                    is_active=True,
                    depot_lat__isnull=False,
                    depot_lon__isnull=False
                ).prefetch_related('skills')
                
                if not pending_requests.exists():
                    messages.warning(request, 'No pending service requests found.')
                elif not active_technicians.exists():
                    messages.error(request, 'No active technicians with valid depot coordinates.')
                else:
                    # Run OR-Tools solver
                    try:
                        routing_service = RoutingService()
                        
                        # Get assignments and unserved requests
                        assignments_data, unserved, total_travel = routing_service.solve(
                            list(active_technicians),
                            list(pending_requests),
                            timezone.make_aware(datetime.combine(assigned_date, datetime.min.time()))
                        )
                        
                        # Save assignments
                        saved_count = 0
                        for assignment_data in assignments_data:
                            # Create assignment
                            assignment = Assignment.objects.create(
                                service_request=assignment_data['service_request'],
                                technician=assignment_data['technician'],
                                assigned_date=assigned_date,
                                sequence_order=assignment_data['sequence_order'],
                                planned_start=assignment_data['planned_start'],
                                planned_finish=assignment_data['planned_finish'],
                                travel_time_minutes=assignment_data.get('travel_time', 0.0),
                                status='assigned'
                            )
                            
                            # Update service request status
                            assignment_data['service_request'].status = 'assigned'
                            assignment_data['service_request'].save()
                            saved_count += 1
                        
                        messages.success(
                            request, 
                            f'Successfully assigned {saved_count} jobs. Total travel time: {total_travel:.1f} minutes.'
                        )
                        
                        if unserved:
                            messages.warning(
                                request,
                                f'{len(unserved)} requests could not be assigned (unserved).'
                            )
                        
                        # Redirect to assignments list for the selected date
                        return redirect(f'/admin/core/assignment/?assigned_date={assigned_date}')
                        
                    except Exception as e:
                        messages.error(request, f'Assignment failed: {str(e)}')
        
        # GET request - show assignment form
        pending_count = ServiceRequest.objects.filter(status='pending').count()
        active_tech_count = Technician.objects.filter(
            is_active=True, 
            depot_lat__isnull=False, 
            depot_lon__isnull=False
        ).count()
        
        context = {
            **admin.site.each_context(request),
            'pending_count': pending_count,
            'active_tech_count': active_tech_count,
            'today': timezone.now().date(),
            'pending_requests': ServiceRequest.objects.filter(status='pending')[:10],
            'title': 'Assign Jobs',
            'opts': {'app_label': 'core', 'model_name': 'assignment'},
        }
        
        return render(request, 'core/admin_assign.html', context)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = ['user', 'depot_address', 'availability_display', 'capacity_minutes', 'skills_display', 'is_active']
    list_filter = ['is_active', 'skills']
    search_fields = ['user__username', 'depot_address']
    filter_horizontal = ['skills']
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Location', {'fields': ('depot_address', 'depot_lat', 'depot_lon')}),
        ('Availability', {'fields': ('shift_start', 'shift_end', 'capacity_minutes')}),
        ('Skills & Styling', {'fields': ('skills', 'color_hex')}),
        ('Status', {'fields': ('is_active',)}),
    )
    
    def skills_display(self, obj):
        """Display skills as comma-separated list"""
        skills = obj.skills.all()
        if skills:
            skill_names = ', '.join([skill.name for skill in skills])
            return skill_names
        return "No skills"
    skills_display.short_description = 'Skills'
    
    def availability_display(self, obj):
        """Display shift times, location, and next assignment dates"""
        from django.utils.html import format_html
        
        # Get depot address and coordinates
        depot = obj.depot_address or "No depot"
        coords = ""
        if obj.depot_lat and obj.depot_lon:
            coords = f" ({obj.depot_lat:.4f}, {obj.depot_lon:.4f})"
        
        # Get shift times
        if obj.shift_start and obj.shift_end:
            shift = f"{obj.shift_start.strftime('%H:%M')} - {obj.shift_end.strftime('%H:%M')}"
        else:
            shift = "No shift times"
        
        # Get upcoming assignments dates
        from core.models import Assignment
        upcoming = Assignment.objects.filter(
            technician=obj,
            status__in=['assigned', 'in_progress']
        ).values_list('assigned_date', flat=True).distinct().order_by('assigned_date')[:3]
        
        dates_str = ", ".join([date.strftime('%Y-%m-%d') for date in upcoming]) if upcoming else "No upcoming assignments"
        
        # Format HTML
        html = f'<div style="font-size: 11px;">'
        html += f'<div><strong>⌚ Shift:</strong> {shift}</div>'
        html += f'<div><strong>📍 Location:</strong> {depot}{coords}</div>'
        html += f'<div><strong>📅 Upcoming:</strong> {dates_str}</div>'
        html += f'<div><strong>⚡ Capacity:</strong> {obj.capacity_minutes // 60}h {obj.capacity_minutes % 60}m</div>'
        html += '</div>'
        
        return format_html(html)
    availability_display.short_description = 'Availability & Location'


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0
    fields = ['technician', 'assigned_date', 'sequence_order', 'planned_start', 'status']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(technician__isnull=False)


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer', 'address', 'status', 'priority', 'assigned_technician', 'assigned_skill_info']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['name', 'customer__username', 'address']
    inlines = [AssignmentInline]
    fieldsets = (
        ('Customer Info', {'fields': ('customer', 'name')}),
        ('Location', {'fields': ('address', 'lat', 'lon')}),
        ('Service Details', {'fields': ('service_minutes', 'window_start', 'window_end', 'required_skill')}),
        ('Status', {'fields': ('priority', 'status', 'notes')}),
    )
    
    actions = ['mark_as_pending', 'mark_as_assigned']
    
    def assigned_technician(self, obj):
        """Show assigned technician"""
        assignment = obj.assignments.filter(status__in=['assigned', 'in_progress']).first()
        if assignment and assignment.technician:
            return assignment.technician.user.username
        return "-"
    assigned_technician.short_description = 'Assigned To'
    
    def assigned_skill_info(self, obj):
        """Show skill for this service request"""
        if obj.required_skill:
            return obj.required_skill.name
        return "-"
    assigned_skill_info.short_description = 'Required Skill'
    
    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending')
        self.message_user(request, f"Marked {queryset.count()} requests as pending.")
    mark_as_pending.short_description = "Mark as pending"
    
    def mark_as_assigned(self, request, queryset):
        queryset.update(status='assigned')
        self.message_user(request, f"Marked {queryset.count()} requests as assigned.")
    mark_as_assigned.short_description = "Mark as assigned"


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['service_request', 'technician', 'assigned_date', 'sequence_order', 'status', 
                    'skills_comparison', 'time_window_status']
    list_filter = ['status', 'assigned_date']
    search_fields = ['service_request__name']
    date_hierarchy = 'assigned_date'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only show assignments with valid technicians
        return qs.filter(technician__isnull=False)
    fieldsets = (
        ('Job Info', {'fields': ('service_request', 'technician', 'assigned_date', 'sequence_order')}),
        ('Timing', {'fields': ('planned_start', 'planned_finish', 'actual_start', 'actual_finish')}),
        ('Status', {'fields': ('status', 'travel_time_minutes')}),
    )
    
    def skills_comparison(self, obj):
        """Show required skills vs technician's skills"""
        if not obj.technician:
            return "-"
        
        info = obj.get_skills_match_info()
        if not info:
            return "-"
        
        required = ', '.join(info['required']) or 'None'
        tech_has = ', '.join(info['tech_has']) or 'None'
        
        if info['is_match']:
            icon = '✓'
            color = 'green'
        else:
            icon = '✗'
            color = 'red'
            missing = ', '.join(info['missing']) if info['missing'] else 'All matched'
        
        html = f'<div style="font-size: 12px;">'
        html += f'<div><strong>Required:</strong> {required}</div>'
        html += f'<div><strong>Technician Has:</strong> {tech_has}</div>'
        if not info['is_match'] and info['missing']:
            html += f'<div style="color: red;"><strong>Missing:</strong> {", ".join(info["missing"])}</div>'
        html += f'</div>'
        
        return format_html(html)
    skills_comparison.short_description = 'Skills'
    
    def time_window_status(self, obj):
        """Show time window match status"""
        if not obj.technician:
            return "-"
        
        info = obj.get_time_window_info()
        if not info:
            return "-"
        
        if info['is_within_window']:
            icon = '✓'
            status_text = 'Within Window'
            color = 'green'
        else:
            icon = '✗'
            status_text = 'Outside Window'
            color = 'red'
        
        customer_start = info['customer_window_start'].strftime('%H:%M')
        customer_end = info['customer_window_end'].strftime('%H:%M')
        tech_start = info['tech_shift_start'].strftime('%H:%M')
        tech_end = info['tech_shift_end'].strftime('%H:%M')
        
        html = f'<div style="font-size: 12px;">'
        html += f'<div style="color: {color};"><strong>{icon} {status_text}</strong></div>'
        html += f'<div><strong>Customer needs:</strong> {customer_start} - {customer_end}</div>'
        html += f'<div><strong>Tech available:</strong> {tech_start} - {tech_end}</div>'
        html += f'</div>'
        
        return format_html(html)
    time_window_status.short_description = 'Time Window'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        from django.urls import reverse
        assign_url = reverse('core:admin_assign')
        map_url = '/core/admin/map/'
        
        buttons = format_html(
            '<div style="margin: 10px 0;">'
            '<a href="{}" class="button" style="background: #417690; color: white; padding: 10px 20px; text-decoration: none; font-weight: bold; font-size: 14px; display: inline-block; margin-right: 10px;">🚀 Run OR-Tools Assignment</a>'
            '<a href="{}" class="button" style="background: #34A853; color: white; padding: 10px 20px; text-decoration: none; font-weight: bold; font-size: 14px; display: inline-block;">📍 View Routes on Map</a>'
            '</div>',
            assign_url,
            map_url
        )
        extra_context['assignment_button'] = buttons
        return super().changelist_view(request, extra_context)


@admin.register(GoogleMapsConfig)
class GoogleMapsConfigAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one instance
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton
        return False


# Custom admin site to add assignment link
admin.site.site_header = "Tech Routing System"
admin.site.site_title = "Tech Routing Admin"
admin.site.index_title = "Assignment Dashboard"


def bulk_upload_view(request):
    """View for bulk uploading users via Excel or manual entry"""
    from core.forms import BulkUploadForm
    from core.services.bulk_upload import BulkUploadService
    from django.http import FileResponse
    from django.conf import settings
    import os
    
    if request.method == 'POST':
        mode = request.POST.get('mode', 'upload')
        
        # Handle AJAX requests for step-by-step creation
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            from accounts.models import User
            
            if mode == 'manual_account':
                # Create user account only
                try:
                    username = request.POST.get('username_0', '')
                    email = request.POST.get('email_0', '')
                    password = request.POST.get('password_0', 'Welcome123')
                    phone = request.POST.get('phone_0', '')
                    user_type = request.POST.get('type_0', 'CUSTOMER').upper()
                    
                    print(f"Creating user account with role: {user_type}")
                    print(f"Username: {username}, Email: {email}")
                    
                    # Get or create user
                    user, created = BulkUploadService()._get_or_create_user_manual(
                        username, email, password, phone, user_type
                    )
                    
                    print(f"User created: {user.username}, Role: {user.role}")
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Account created successfully',
                        'user_id': user.id
                    })
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'message': str(e)
                    })
            
            elif mode == 'manual_service':
                # Create service request only
                try:
                    from core.models import ServiceRequest
                    from maps.services import GeocodingService
                    
                    # Get user_id from previous step
                    user_id = request.POST.get('user_id_0')
                    if not user_id:
                        return JsonResponse({
                            'success': False,
                            'message': 'User ID not found. Please create account first.'
                        })
                    
                    # Get user
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    try:
                        user = User.objects.get(id=user_id)
                    except User.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'message': 'User not found'
                        })
                    
                    # Get service request fields
                    address = request.POST.get('address_0', '')
                    service_type = request.POST.get('service_type_0', '')
                    service_minutes = request.POST.get('service_minutes_0', '60')
                    window_start = request.POST.get('window_start_0', '')
                    window_end = request.POST.get('window_end_0', '')
                    priority = request.POST.get('priority_0', 'medium')
                    notes = request.POST.get('notes_0', '')
                    required_skill_name = request.POST.get('required_skill_0', '')
                    
                    # Geocode address
                    geocoding = GeocodingService()
                    try:
                        coords, method = geocoding.geocode(address)
                        if not coords:
                            raise ValueError(f"Could not geocode address: {address}")
                        lat, lon = coords
                    except Exception as e:
                        return JsonResponse({
                            'success': False,
                            'message': f'Geocoding failed: {str(e)}'
                        })
                    
                    # Parse datetime fields
                    from datetime import datetime
                    from django.utils import timezone
                    
                    try:
                        window_start_dt = timezone.make_aware(datetime.fromisoformat(window_start.replace('Z', '+00:00')))
                        window_end_dt = timezone.make_aware(datetime.fromisoformat(window_end.replace('Z', '+00:00')))
                    except Exception as e:
                        return JsonResponse({
                            'success': False,
                            'message': f'Invalid date format: {str(e)}'
                        })
                    
                    # Create service request
                    priority_map = {'high': 1, 'medium': 2, 'low': 3}
                    priority_int = priority_map.get(priority, 2)
                    
                    service_request = ServiceRequest.objects.create(
                        customer=user,
                        name=service_type or 'Service Request',
                        address=address,
                        lat=lat,
                        lon=lon,
                        service_minutes=int(service_minutes),
                        window_start=window_start_dt,
                        window_end=window_end_dt,
                        priority=priority_int,
                        status='pending',
                        notes=notes
                    )
                    
                    # Add required skill
                    if required_skill_name:
                        from core.models import Skill
                        skill, _ = Skill.objects.get_or_create(name=required_skill_name, defaults={'is_active': True})
                        service_request.required_skill = skill
                        service_request.save()
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Service request created successfully'
                    })
                    
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    return JsonResponse({
                        'success': False,
                        'message': str(e)
                    })
        
        if mode == 'manual':
            # Process manual entry
            service = BulkUploadService()
            results = service.process_manual_entries(request.POST)
            
            # Display results
            if results['errors']:
                for error in results['errors']:
                    messages.error(request, error)
            
            if results['warnings']:
                for warning in results['warnings']:
                    messages.warning(request, warning)
            
            # Success message
            success_msg = (
                f"Manual entry complete: {len(results['created_users'])} created, "
                f"{len(results['updated_users'])} updated, "
                f"{len(results['created_requests'])} service requests created, "
                f"{len(results['created_technicians'])} technician profiles created."
            )
            messages.success(request, success_msg)
            
            return redirect('core:bulk_upload')
        
        else:
            # Process Excel upload
            form = BulkUploadForm(request.POST, request.FILES)
            
            if form.is_valid():
                excel_file = form.cleaned_data['excel_file']
                
                # Process the file
                service = BulkUploadService()
                results = service.process_excel_file(excel_file)
                
                # Display results
                if results['errors']:
                    for error in results['errors']:
                        messages.error(request, error)
                
                if results['warnings']:
                    for warning in results['warnings']:
                        messages.warning(request, warning)
                
                # Success message
                success_msg = (
                    f"Upload complete: {len(results['created_users'])} created, "
                    f"{len(results['updated_users'])} updated, "
                    f"{len(results['created_requests'])} service requests created, "
                    f"{len(results['created_technicians'])} technician profiles created."
                )
                messages.success(request, success_msg)
                
                return redirect('core:bulk_upload')
    else:
        form = BulkUploadForm()
    
    # Get Google Maps API key for autocomplete
    config = GoogleMapsConfig.load()
    
    # Get all active skills for dropdown
    from core.models import Skill
    all_skills = Skill.objects.filter(is_active=True).order_by('name')
    skills_data = [{'id': skill.id, 'name': skill.name} for skill in all_skills]
    
    context = {
        'form': form,
        'title': 'Bulk Upload Users',
        'opts': {'app_label': 'core', 'model_name': 'bulk_upload'},
        'api_key': config.api_key if config else '',
        'skills': skills_data,
    }
    
    return render(request, 'admin/bulk_upload.html', context)
