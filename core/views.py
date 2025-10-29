from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from core.models import Technician, ServiceRequest, Assignment, GoogleMapsConfig
from routing.services import RoutingService


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_assign_view(request):
    """Admin assignment interface - trigger OR-Tools matching"""
    config = GoogleMapsConfig.load()
    
    if request.method == 'POST':
        # Get selected date
        assigned_date_str = request.POST.get('assigned_date', '')
        if not assigned_date_str:
            messages.error(request, 'Please select a date.')
            return redirect('core:admin_assign')
        
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
            return redirect('core:admin_assign')
        
        if not active_technicians.exists():
            messages.error(request, 'No active technicians with valid depot coordinates.')
            return redirect('core:admin_assign')
        
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
            updated_count = 0
            for assignment_data in assignments_data:
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
            import traceback
            error_details = traceback.format_exc()
            print(f"\n{'='*80}")
            print(f"ASSIGNMENT ERROR")
            print(f"{'='*80}")
            print(f"Error: {str(e)}")
            print(f"Traceback:")
            print(error_details)
            print(f"{'='*80}\n")
            messages.error(request, f'Assignment failed: {str(e)}')
            return redirect('core:admin_assign')
    
    # GET request - show assignment form
    from datetime import datetime, date, timedelta
    
    pending_count = ServiceRequest.objects.filter(status='pending').count()
    active_technicians = Technician.objects.filter(
        is_active=True, 
        depot_lat__isnull=False, 
        depot_lon__isnull=False
    ).prefetch_related('skills', 'user')
    
    active_tech_count = active_technicians.count()
    
    # Get pending requests with details
    pending_requests = ServiceRequest.objects.filter(
        status='pending'
    ).select_related('required_skill', 'customer').order_by('window_start')[:20]
    
    # Get technician availability info
    technicians_data = []
    for tech in active_technicians:
        skills_list = [skill.name for skill in tech.skills.all()]
        
        # Get existing assignments for today and tomorrow
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        today_assignments = Assignment.objects.filter(
            technician=tech,
            assigned_date=today,
            status__in=['assigned', 'in_progress']
        ).select_related('service_request')
        
        tomorrow_assignments = Assignment.objects.filter(
            technician=tech,
            assigned_date=tomorrow,
            status__in=['assigned', 'in_progress']
        ).select_related('service_request')
        
        technicians_data.append({
            'technician': tech,
            'username': tech.user.username,
            'skills': skills_list,
            'shift': f"{tech.shift_start.strftime('%H:%M')} - {tech.shift_end.strftime('%H:%M')}",
            'capacity': f"{tech.capacity_minutes // 60}h {tech.capacity_minutes % 60}m",
            'today_assignments': today_assignments.count(),
            'tomorrow_assignments': tomorrow_assignments.count(),
            'is_available_today': today_assignments.count() == 0,
            'is_available_tomorrow': tomorrow_assignments.count() == 0,
        })
    
    # Get pending requests with required skills and dates
    pending_requests_data = []
    for req in pending_requests:
        required_skill = req.required_skill.name if req.required_skill else 'No skill required'
        window_date = req.window_start.date() if req.window_start else None
        
        pending_requests_data.append({
            'request': req,
            'name': req.name,
            'customer': req.customer.username,
            'required_skill': required_skill,
            'window_date': window_date,
            'window_start': req.window_start.strftime('%Y-%m-%d %H:%M') if req.window_start else 'N/A',
            'window_end': req.window_end.strftime('%Y-%m-%d %H:%M') if req.window_end else 'N/A',
            'priority': req.get_priority_display() if hasattr(req, 'get_priority_display') else req.priority,
        })
    
    context = {
        'pending_count': pending_count,
        'active_tech_count': active_tech_count,
        'today': timezone.now().date(),
        'pending_requests': pending_requests,  # Keep for backward compatibility
        'technicians_data': technicians_data,
        'pending_requests_data': pending_requests_data,
    }
    
    return render(request, 'core/admin_assign.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_map_view(request):
    """Admin map view showing all technician routes"""
    import json
    
    assigned_date_str = request.GET.get('date', str(timezone.now().date()))
    
    try:
        from datetime import datetime
        assigned_date = datetime.strptime(assigned_date_str, '%Y-%m-%d').date()
    except:
        assigned_date = timezone.now().date()
    
    # Get assignments for the selected date
    assignments = Assignment.objects.filter(assigned_date=assigned_date).order_by(
        'technician', 'sequence_order'
    ).select_related('technician', 'service_request')
    
    # Build routes data for JavaScript
    routes_data = []
    for tech in Technician.objects.filter(is_active=True, depot_lat__isnull=False):
        tech_assignments = [a for a in assignments if a.technician == tech]
        if not tech_assignments:
            continue
        
        stops = []
        for assign in tech_assignments:
            stops.append({
                'position': {'lat': assign.service_request.lat, 'lng': assign.service_request.lon},
                'customer': assign.service_request.name,
                'sequence': assign.sequence_order
            })
        
        routes_data.append({
            'technician': tech.user.username,
            'color': tech.color_hex,
            'depot': {'lat': tech.depot_lat, 'lng': tech.depot_lon},
            'stops': stops,
            'path': []  # We'll use simple polylines
        })
    
    config = GoogleMapsConfig.load()
    context = {
        'routes': {},
        'routes_json': json.dumps(routes_data),
        'selected_date': assigned_date,
        'api_key': config.api_key if config and config.api_key else '',
    }
    
    return render(request, 'core/admin_map.html', context)
