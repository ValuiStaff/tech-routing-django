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
                        
                        print(f"\nDEBUG: assignments_data count: {len(assignments_data)}")
                        
                        # Save assignments
                        saved_count = 0
                        updated_count = 0
                        for assignment_data in assignments_data:
                            print(f"DEBUG: Processing assignment for {assignment_data['service_request'].name}")
                            
                            # Check if assignment already exists for this date
                            existing = Assignment.objects.filter(
                                service_request=assignment_data['service_request'],
                                assigned_date=assigned_date
                            ).first()
                            
                            if existing:
                                # Update existing assignment
                                existing.technician = assignment_data['technician']
                                existing.sequence_order = assignment_data['sequence_order']
                                existing.planned_start = assignment_data['planned_start']
                                existing.planned_finish = assignment_data['planned_finish']
                                existing.travel_time_minutes = assignment_data.get('travel_time', 0.0)
                                existing.status = 'assigned'
                                existing.save()
                                updated_count += 1
                                print(f"DEBUG: Updated existing assignment")
                            else:
                                # Create new assignment
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
                                saved_count += 1
                                print(f"DEBUG: Created new assignment")
                            
                            # Update service request status
                            assignment_data['service_request'].status = 'assigned'
                            assignment_data['service_request'].save()
                        
                        if saved_count > 0 and updated_count > 0:
                            messages.success(
                                request, 
                                f'Successfully created {saved_count} new assignments and updated {updated_count} existing assignments. Total travel time: {total_travel:.1f} minutes.'
                            )
                        elif saved_count > 0:
                            messages.success(
                                request, 
                                f'Successfully assigned {saved_count} jobs. Total travel time: {total_travel:.1f} minutes.'
                            )
                        elif updated_count > 0:
                            messages.success(
                                request, 
                                f'Updated {updated_count} existing assignments. Total travel time: {total_travel:.1f} minutes.'
                            )
                        else:
                            messages.info(request, 'No assignments created or updated.')
                        
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
        
        # Get all assignment dates with details
        from core.models import Assignment
        from django.utils import timezone
        from datetime import date
        
        today = timezone.now().date()
        
        # Get all assignments grouped by date
        all_assignments = Assignment.objects.filter(technician=obj).order_by('assigned_date')
        
        # Group assignments by date
        assignments_by_date = {}
        for assignment in all_assignments:
            assign_date = assignment.assigned_date
            if assign_date not in assignments_by_date:
                assignments_by_date[assign_date] = []
            assignments_by_date[assign_date].append(assignment)
        
        # Separate into today, upcoming, and past
        today_assignments = assignments_by_date.get(today, [])
        upcoming_dates = [d for d in sorted(assignments_by_date.keys()) if d > today]
        past_dates = [d for d in sorted(assignments_by_date.keys(), reverse=True) if d < today]
        
        # Format dates display
        dates_html = []
        
        # Show today's assignments
        if today_assignments:
            today_count = len(today_assignments)
            active = [a for a in today_assignments if a.status in ['assigned', 'in_progress']]
            status = today_assignments[0].status if today_assignments else 'assigned'
            status_color = {'assigned': '#2196F3', 'in_progress': '#FF9800', 'completed': '#4CAF50', 'cancelled': '#F44336'}.get(status, '#666')
            dates_html.append(
                f'<div><strong>📅 Today ({today.strftime("%Y-%m-%d")}):</strong> '
                f'<span style="color: {status_color}; font-weight: bold;">{today_count} job(s) - {status.replace("_", " ").upper()}</span></div>'
            )
        
        # Show upcoming dates (next 10)
        if upcoming_dates:
            upcoming_str = ", ".join([d.strftime('%Y-%m-%d') for d in upcoming_dates[:10]])
            if len(upcoming_dates) > 10:
                upcoming_str += f" (+{len(upcoming_dates) - 10} more)"
            
            # Count jobs per date
            job_counts = []
            for d in upcoming_dates[:5]:
                count = len(assignments_by_date[d])
                job_counts.append(f"{d.strftime('%m-%d')}({count})")
            
            dates_html.append(
                f'<div><strong>📅 Upcoming Dates:</strong> {", ".join(job_counts)}'
                + (f" ... ({len(upcoming_dates)} dates total)" if len(upcoming_dates) > 5 else "")
                + '</div>'
            )
        
        # Show recent past dates (last 5)
        if past_dates:
            recent_past = past_dates[:5]
            recent_str = ", ".join([d.strftime('%Y-%m-%d') for d in recent_past])
            dates_html.append(
                f'<div><strong>📅 Recent Past:</strong> <span style="color: #999; font-size: 10px;">{recent_str}</span></div>'
            )
        
        if not dates_html:
            dates_html.append('<div><strong>📅 No assignments scheduled</strong></div>')
        
        # Format HTML
        html = f'<div style="font-size: 11px; line-height: 1.6;">'
        html += f'<div><strong>⌚ Daily Shift:</strong> {shift}</div>'
        html += f'<div><strong>📍 Depot:</strong> {depot}{coords}</div>'
        html += ''.join(dates_html)
        html += f'<div><strong>⚡ Capacity:</strong> {obj.capacity_minutes // 60}h {obj.capacity_minutes % 60}m/day</div>'
        html += '</div>'
        
        return format_html(html)
    availability_display.short_description = 'Availability & Dates'


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
    list_display = ['name', 'customer', 'window_date', 'window_time', 'address', 'status', 'priority', 'assigned_technician', 'assigned_skill_info']
    list_filter = ['status', 'priority', 'created_at', 'window_start']
    search_fields = ['name', 'customer__username', 'address']
    inlines = [AssignmentInline]
    fieldsets = (
        ('Customer Info', {'fields': ('customer', 'name')}),
        ('Location', {'fields': ('address', 'lat', 'lon')}),
        ('Service Details', {'fields': ('service_minutes', 'window_start', 'window_end', 'required_skill')}),
        ('Status', {'fields': ('priority', 'status', 'notes')}),
    )
    
    actions = ['bulk_edit', 'edit_multiple', 'mark_as_pending', 'mark_as_assigned', 'mark_as_completed', 'mark_as_cancelled']
    
    def edit_multiple(self, request, queryset):
        """Edit multiple service requests on a single page"""
        from django import forms
        from django.http import HttpResponseRedirect
        from django.forms import formset_factory
        from django.utils import timezone as tz
        from datetime import datetime
        
        class ServiceRequestEditForm(forms.Form):
            """Form for editing a single service request"""
            id = forms.IntegerField(widget=forms.HiddenInput())
            name = forms.CharField(max_length=200, required=True)
            status = forms.ChoiceField(choices=ServiceRequest.STATUS_CHOICES, required=True)
            priority = forms.ChoiceField(choices=ServiceRequest.PRIORITY_CHOICES, required=True)
            required_skill = forms.ModelChoiceField(
                queryset=Skill.objects.filter(is_active=True),
                required=False
            )
            service_minutes = forms.IntegerField(min_value=1, required=True)
            window_start = forms.DateTimeField(
                required=True,
                widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
            )
            window_end = forms.DateTimeField(
                required=True,
                widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
            )
            address = forms.CharField(max_length=500, required=True)
            notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
        
        # Use explicit prefix to ensure consistent field names
        ServiceRequestFormSet = formset_factory(
            ServiceRequestEditForm, 
            extra=0, 
            can_delete=False,
            formset=forms.BaseFormSet
        )
        
        # Preserve selected IDs - store in session if queryset is provided
        selected_ids = []
        if queryset.exists():
            selected_ids = list(queryset.values_list('id', flat=True))
            request.session['edit_multiple_ids'] = selected_ids
        
        # Get selected IDs from POST/GET or session
        if request.method == 'POST':
            if 'selected_ids' in request.POST and request.POST['selected_ids']:
                selected_ids = [int(x) for x in request.POST['selected_ids'].split(',') if x.strip()]
            elif 'edit_multiple_ids' in request.session:
                selected_ids = request.session['edit_multiple_ids']
        else:
            if 'ids' in request.GET:
                selected_ids = [int(x) for x in request.GET['ids'].split(',') if x.strip()]
            elif 'edit_multiple_ids' in request.session:
                selected_ids = request.session['edit_multiple_ids']
            elif not selected_ids and queryset.exists():
                selected_ids = list(queryset.values_list('id', flat=True))
        
        # Get queryset from selected IDs
        if selected_ids:
            queryset = ServiceRequest.objects.filter(id__in=selected_ids).order_by('id')
        elif queryset.exists():
            # Use the provided queryset
            queryset = queryset.order_by('id')
            selected_ids = list(queryset.values_list('id', flat=True))
        
        # Ensure we have selected IDs
        if not selected_ids:
            messages.error(request, 'No service requests selected. Please select items from the list and try again.')
            return HttpResponseRedirect(reverse('admin:core_servicerequest_changelist'))
        
        if request.method == 'POST':
            # Get the POST data
            post_data = request.POST.copy()
            
            # Ensure management form fields are present
            if 'form-TOTAL_FORMS' not in post_data or 'form-INITIAL_FORMS' not in post_data:
                # Try to determine count from selected_ids or form fields
                if 'selected_ids' in post_data and post_data['selected_ids']:
                    count = len([x for x in post_data['selected_ids'].split(',') if x.strip()])
                else:
                    # Count form indices from POST data
                    form_indices = set()
                    for key in post_data.keys():
                        if key.startswith('form-') and '-' in key:
                            parts = key.split('-')
                            if len(parts) >= 2 and parts[1].isdigit():
                                form_indices.add(int(parts[1]))
                    count = len(form_indices) if form_indices else len(selected_ids) if selected_ids else 0
                
                if count > 0:
                    post_data['form-TOTAL_FORMS'] = str(count)
                    post_data['form-INITIAL_FORMS'] = str(count)
                    post_data['form-MIN_NUM_FORMS'] = '0'
                    post_data['form-MAX_NUM_FORMS'] = '1000'
                else:
                    # No forms to process
                    messages.error(request, 'No service requests selected. Please select items and try again.')
                    return HttpResponseRedirect(reverse('admin:core_servicerequest_changelist'))
            
            # Ensure queryset is available from selected_ids
            if not queryset.exists() and selected_ids:
                queryset = ServiceRequest.objects.filter(id__in=selected_ids).order_by('id')
            
            if not queryset.exists():
                messages.error(request, 'No service requests found. Please select items and try again.')
                return HttpResponseRedirect(reverse('admin:core_servicerequest_changelist'))
            
            formset = ServiceRequestFormSet(post_data)
            
            if not formset.is_valid():
                # If formset is invalid, show errors and re-render with POST data
                # Ensure queryset is available
                if not queryset.exists() and selected_ids:
                    queryset = ServiceRequest.objects.filter(id__in=selected_ids).order_by('id')
                
                # Re-initialize formset with POST data AND initial data to show errors properly
                if queryset.exists():
                    initial_data = []
                    for sr in queryset:
                        initial_data.append({
                            'id': sr.id,
                            'name': sr.name,
                            'status': sr.status,
                            'priority': sr.priority,
                            'required_skill': sr.required_skill,
                            'service_minutes': sr.service_minutes,
                            'window_start': sr.window_start.strftime('%Y-%m-%dT%H:%M') if sr.window_start else '',
                            'window_end': sr.window_end.strftime('%Y-%m-%dT%H:%M') if sr.window_end else '',
                            'address': sr.address,
                            'notes': sr.notes or '',
                        })
                    formset = ServiceRequestFormSet(initial=initial_data, data=post_data)
                else:
                    formset = ServiceRequestFormSet(data=post_data)
            else:
                # Formset is valid, process the data
                updated_count = 0
                for form in formset:
                    if form.cleaned_data:
                        try:
                            service_request = ServiceRequest.objects.get(id=form.cleaned_data['id'])
                            service_request.name = form.cleaned_data['name']
                            service_request.status = form.cleaned_data['status']
                            service_request.priority = int(form.cleaned_data['priority'])
                            service_request.service_minutes = form.cleaned_data['service_minutes']
                            service_request.window_start = form.cleaned_data['window_start']
                            service_request.window_end = form.cleaned_data['window_end']
                            service_request.address = form.cleaned_data['address']
                            service_request.notes = form.cleaned_data['notes']
                            if form.cleaned_data['required_skill']:
                                service_request.required_skill = form.cleaned_data['required_skill']
                            service_request.save()
                            updated_count += 1
                        except ServiceRequest.DoesNotExist:
                            continue
                
                messages.success(
                    request,
                    f"Successfully updated {updated_count} service request(s)."
                )
                return HttpResponseRedirect(reverse('admin:core_servicerequest_changelist'))
        
        # GET request or form invalid - ensure queryset exists
        if not queryset.exists():
            if selected_ids:
                queryset = ServiceRequest.objects.filter(id__in=selected_ids).order_by('id')
            elif 'edit_multiple_ids' in request.session:
                session_ids = request.session['edit_multiple_ids']
                queryset = ServiceRequest.objects.filter(id__in=session_ids).order_by('id')
                selected_ids = session_ids
        
        if not queryset.exists():
            messages.error(request, 'No service requests found. Please select items and try again.')
            return HttpResponseRedirect(reverse('admin:core_servicerequest_changelist'))
        
        # Initialize formset with existing data
        initial_data = []
        queryset_list = list(queryset)  # Convert to list to preserve order
        for sr in queryset_list:
            initial_data.append({
                'id': sr.id,
                'name': sr.name,
                'status': sr.status,
                'priority': sr.priority,
                'required_skill': sr.required_skill,
                'service_minutes': sr.service_minutes,
                'window_start': sr.window_start.strftime('%Y-%m-%dT%H:%M') if sr.window_start else '',
                'window_end': sr.window_end.strftime('%Y-%m-%dT%H:%M') if sr.window_end else '',
                'address': sr.address,
                'notes': sr.notes or '',
            })
        formset = ServiceRequestFormSet(initial=initial_data)
        
        # Create a list of tuples (form, service_request) for easier template rendering
        queryset_list = list(queryset)
        form_service_pairs = []
        for i, form in enumerate(formset):
            if i < len(queryset_list):
                form_service_pairs.append((form, queryset_list[i]))
        
        # Store selected IDs for form submission
        selected_ids = ','.join([str(obj.id) for obj in queryset_list]) if queryset_list else ''
        
        # Get Google Maps API key for autocomplete
        config = GoogleMapsConfig.load()
        
        context = {
            'title': 'Edit Multiple Service Requests',
            'formset': formset,
            'form_service_pairs': form_service_pairs,
            'queryset': queryset,
            'selected_count': queryset.count(),
            'selected_ids': selected_ids,
            'opts': self.model._meta,
            'api_key': config.api_key if config and config.api_key else '',
        }
        
        return render(request, 'admin/core/servicerequest/edit_multiple.html', context)
    edit_multiple.short_description = "Edit multiple service requests on one page"
    
    def bulk_edit(self, request, queryset):
        """Bulk edit multiple service requests"""
        from django import forms
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        
        class BulkEditForm(forms.Form):
            """Form for bulk editing service requests"""
            status = forms.ChoiceField(
                choices=[('', '--- Keep Current ---')] + list(ServiceRequest.STATUS_CHOICES),
                required=False,
                help_text='Change status for all selected requests (leave blank to keep current)'
            )
            priority = forms.ChoiceField(
                choices=[('', '--- Keep Current ---')] + list(ServiceRequest.PRIORITY_CHOICES),
                required=False,
                help_text='Change priority for all selected requests (leave blank to keep current)'
            )
            required_skill = forms.ModelChoiceField(
                queryset=Skill.objects.filter(is_active=True),
                required=False,
                empty_label='--- Keep Current ---',
                help_text='Change required skill for all selected requests (leave blank to keep current)'
            )
            service_minutes = forms.IntegerField(
                required=False,
                min_value=1,
                help_text='Change service duration in minutes (leave blank to keep current)'
            )
            notes_append = forms.CharField(
                widget=forms.Textarea(attrs={'rows': 3}),
                required=False,
                help_text='Append this note to existing notes for all selected requests'
            )
        
        if 'apply' in request.POST:
            form = BulkEditForm(request.POST)
            if form.is_valid():
                updated_count = 0
                
                for service_request in queryset:
                    changed = False
                    
                    # Update status
                    if form.cleaned_data['status']:
                        service_request.status = form.cleaned_data['status']
                        changed = True
                    
                    # Update priority
                    if form.cleaned_data['priority']:
                        service_request.priority = int(form.cleaned_data['priority'])
                        changed = True
                    
                    # Update required skill
                    if form.cleaned_data['required_skill']:
                        service_request.required_skill = form.cleaned_data['required_skill']
                        changed = True
                    
                    # Update service minutes
                    if form.cleaned_data['service_minutes']:
                        service_request.service_minutes = form.cleaned_data['service_minutes']
                        changed = True
                    
                    # Append notes
                    if form.cleaned_data['notes_append']:
                        if service_request.notes:
                            service_request.notes += f"\n\n[Bulk Edit {timezone.now().strftime('%Y-%m-%d %H:%M')}]: {form.cleaned_data['notes_append']}"
                        else:
                            service_request.notes = f"[Bulk Edit {timezone.now().strftime('%Y-%m-%d %H:%M')}]: {form.cleaned_data['notes_append']}"
                        changed = True
                    
                    if changed:
                        service_request.save()
                        updated_count += 1
                
                messages.success(
                    request,
                    f"Successfully updated {updated_count} service request(s)."
                )
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = BulkEditForm()
        
        from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
        
        context = {
            'title': 'Bulk Edit Service Requests',
            'form': form,
            'queryset': queryset,
            'selected_count': queryset.count(),
            'opts': self.model._meta,
            'action_checkbox_name': ACTION_CHECKBOX_NAME,
            'selected_ids': ','.join([str(obj.id) for obj in queryset]),
        }
        
        return render(request, 'admin/core/servicerequest/bulk_edit.html', context)
    bulk_edit.short_description = "Bulk edit selected service requests"
    
    def window_date(self, obj):
        """Show the date of the service window"""
        if obj.window_start:
            return obj.window_start.date()
        return "-"
    window_date.short_description = 'Date'
    window_date.admin_order_field = 'window_start'
    
    def window_time(self, obj):
        """Show the time window"""
        if obj.window_start and obj.window_end:
            start_time = obj.window_start.strftime('%H:%M')
            end_time = obj.window_end.strftime('%H:%M')
            return f"{start_time}-{end_time}"
        return "-"
    window_time.short_description = 'Time Window'
    
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
        """Mark service requests as pending and delete associated assignments"""
        deleted_count = 0
        updated_count = 0
        
        for service_request in queryset:
            # Delete all assignments for this service request
            assignments = Assignment.objects.filter(service_request=service_request)
            if assignments.exists():
                deleted_count += assignments.count()
                assignments.delete()
            
            # Mark as pending
            if service_request.status != 'pending':
                service_request.status = 'pending'
                service_request.save()
                updated_count += 1
        
        messages.success(
            request,
            f"Marked {updated_count} requests as pending and deleted {deleted_count} assignments."
        )
    mark_as_pending.short_description = "Mark as pending (remove assignments)"
    
    def mark_as_assigned(self, request, queryset):
        queryset.update(status='assigned')
        self.message_user(request, f"Marked {queryset.count()} requests as assigned.")
    mark_as_assigned.short_description = "Mark as assigned"
    
    def mark_as_completed(self, request, queryset):
        """Mark service requests as completed and update assignments"""
        updated_count = 0
        
        for request_obj in queryset:
            # Update status
            if request_obj.status != 'completed':
                request_obj.status = 'completed'
                request_obj.save()
                updated_count += 1
            
            # Mark all related assignments as completed
            assignments = Assignment.objects.filter(service_request=request_obj)
            assignments.update(status='completed')
        
        messages.success(
            request,
            f"Marked {updated_count} requests and their assignments as completed."
        )
    mark_as_completed.short_description = "Mark as completed"
    
    def mark_as_cancelled(self, request, queryset):
        """Mark service requests as cancelled and cancel assignments"""
        updated_count = 0
        cancelled_assignments = 0
        
        for request_obj in queryset:
            # Update status
            if request_obj.status != 'cancelled':
                request_obj.status = 'cancelled'
                request_obj.save()
                updated_count += 1
            
            # Cancel all related assignments
            assignments = Assignment.objects.filter(service_request=request_obj)
            if assignments.exists():
                cancelled_assignments += assignments.count()
                assignments.update(status='cancelled')
        
        messages.success(
            request,
            f"Marked {updated_count} requests as cancelled and cancelled {cancelled_assignments} assignments."
        )
    mark_as_cancelled.short_description = "Mark as cancelled"


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['service_request', 'technician_display', 'assigned_date', 'sequence_order', 'status', 
                    'skills_comparison', 'time_window_status']
    list_filter = ['status', 'assigned_date']
    search_fields = ['service_request__name']
    date_hierarchy = 'assigned_date'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Show all assignments, even those with None technicians
        return qs
    
    def technician_display(self, obj):
        """Safely display technician username"""
        if obj.technician and obj.technician.user:
            return obj.technician.user.username
        return "-"
    technician_display.short_description = 'Technician'
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
        
        # Check if arrival is within window
        if info['is_within_window']:
            if info['completes_on_time']:
                icon = '✓'
                status_text = 'On Time'
                color = 'green'
                detail = 'Arrival and completion within window'
            else:
                icon = '⚠'
                status_text = 'Late Completion'
                color = 'orange'
                detail = 'Arrival on time, but completion may exceed window'
        else:
            # Check if too early or too late
            planned_arrival = info['planned_arrival']
            customer_start = info['customer_window_start']
            customer_end = info['customer_window_end']
            
            if planned_arrival < customer_start:
                icon = '⏰'
                status_text = 'Too Early'
                color = 'blue'
                detail = 'Arrival before window starts'
            else:  # planned_arrival > customer_end
                icon = '✗'
                status_text = 'Outside Window'
                color = 'red'
                detail = 'Arrival after window ends'
        
        customer_start_str = info['customer_window_start'].strftime('%Y-%m-%d %H:%M')
        customer_end_str = info['customer_window_end'].strftime('%Y-%m-%d %H:%M')
        planned_arrival_str = info['planned_arrival'].strftime('%Y-%m-%d %H:%M')
        
        html = f'<div style="font-size: 11px; line-height: 1.5;">'
        html += f'<div style="color: {color}; font-weight: bold;"><strong>{icon} {status_text}</strong></div>'
        html += f'<div style="margin-top: 4px;"><strong>Job Window:</strong> {customer_start_str} to {customer_end_str}</div>'
        html += f'<div><strong>Tech Arrival:</strong> {planned_arrival_str}</div>'
        if 'detail' in locals():
            html += f'<div style="color: #666; font-size: 10px; margin-top: 2px;">{detail}</div>'
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
