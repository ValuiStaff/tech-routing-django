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
    pending_count = ServiceRequest.objects.filter(status='pending').count()
    active_tech_count = Technician.objects.filter(
        is_active=True, 
        depot_lat__isnull=False, 
        depot_lon__isnull=False
    ).count()
    
    context = {
        'pending_count': pending_count,
        'active_tech_count': active_tech_count,
        'today': timezone.now().date(),
        'pending_requests': ServiceRequest.objects.filter(status='pending')[:10],
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
