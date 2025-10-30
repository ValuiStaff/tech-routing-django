from django.shortcuts import render, redirect
from django.urls import reverse
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
            filter_date_param = request.GET.get('filter_date', '')
            if filter_date_param:
                return redirect(f'{reverse("core:admin_assign")}?filter_date={filter_date_param}')
            return redirect('core:admin_assign')
        
        if not active_technicians.exists():
            messages.error(request, 'No active technicians with valid depot coordinates.')
            filter_date_param = request.GET.get('filter_date', '')
            if filter_date_param:
                return redirect(f'{reverse("core:admin_assign")}?filter_date={filter_date_param}')
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
            
            # Handle unserved requests with reasons
            if unserved:
                unserved_count = len(unserved)
                reasons_summary = {}
                for item in unserved:
                    reason = item.get('reason_short', 'Unknown reason')
                    if reason not in reasons_summary:
                        reasons_summary[reason] = []
                    reasons_summary[reason].append(item['request'].name)
                
                # Create detailed message
                reasons_text = []
                for reason, requests in reasons_summary.items():
                    if len(requests) == 1:
                        reasons_text.append(f"{reason}: {requests[0]}")
                    else:
                        reasons_text.append(f"{reason}: {len(requests)} requests ({', '.join(requests[:2])}{'...' if len(requests) > 2 else ''})")
                
                detailed_message = f'{unserved_count} request(s) could not be assigned:\n' + '\n'.join(reasons_text)
                
                messages.warning(request, f'{unserved_count} request(s) could not be assigned.')
                
                # Store detailed reasons in session for display on assignment page
                # Filter unserved reasons by assigned_date
                unserved_for_date = [
                    item for item in unserved 
                    if item['request'].window_start and item['request'].window_start.date() == assigned_date
                ]
                
                request.session['unserved_reasons'] = [
                    {
                        'request_name': item['request'].name,
                        'customer': item['request'].customer.username,
                        'reason_short': item.get('reason_short', 'Unknown'),
                        'reason_detail': item.get('reason_detail', 'Unknown reason'),
                        'required_skill': item.get('required_skill', 'None'),
                        'window_start': item['request'].window_start.strftime('%Y-%m-%d %H:%M') if item['request'].window_start else 'N/A',
                        'window_end': item['request'].window_end.strftime('%Y-%m-%d %H:%M') if item['request'].window_end else 'N/A',
                        'window_date': item['request'].window_start.strftime('%Y-%m-%d') if item['request'].window_start else None,
                    }
                    for item in unserved_for_date
                ]
                request.session['unserved_date'] = assigned_date.strftime('%Y-%m-%d')
            
            # Redirect back to assignment page to show results
            filter_date_param = request.GET.get('filter_date', assigned_date.strftime('%Y-%m-%d'))
            return redirect(f'{reverse("core:admin_assign")}?filter_date={filter_date_param}')
            
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
            filter_date_param = request.GET.get('filter_date', '')
            if filter_date_param:
                return redirect(f'{reverse("core:admin_assign")}?filter_date={filter_date_param}')
            return redirect('core:admin_assign')
    
    # GET request - show assignment form
    from datetime import datetime, date, timedelta
    
    # Get filter date from GET parameter, default to today
    filter_date_str = request.GET.get('filter_date', None)
    if filter_date_str:
        try:
            filter_date = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
        except:
            filter_date = timezone.now().date()
    else:
        filter_date = timezone.now().date()
    
    # Get all service requests for the filter date
    # Show requests where the filter_date falls within the time window OR has assignments on that date
    from django.db.models import Q
    
    # Convert filter_date to datetime for comparison
    filter_datetime_start = timezone.make_aware(datetime.combine(filter_date, datetime.min.time()))
    filter_datetime_end = timezone.make_aware(datetime.combine(filter_date, datetime.max.time()))
    
    # Get pending requests where the filter date falls within the window
    # Logic: filter_date is within [window_start, window_end] OR window_start/end date matches filter_date
    pending_requests_query = ServiceRequest.objects.filter(
        status='pending'
    ).filter(
        Q(window_start__lte=filter_datetime_end, window_end__gte=filter_datetime_start) |
        Q(window_start__date=filter_date) |
        Q(window_end__date=filter_date) |
        Q(window_start__isnull=True)  # Include requests without date windows
    ).distinct()
    
    pending_requests = pending_requests_query.select_related(
        'required_skill', 'customer'
    ).order_by('window_start')[:100]  # Increased limit to show all jobs
    
    # Also get all requests that have assignments on this date (regardless of status)
    assigned_request_ids = Assignment.objects.filter(
        assigned_date=filter_date
    ).values_list('service_request_id', flat=True).distinct()
    
    # Get all service requests for this date (pending + assigned)
    all_requests_today = ServiceRequest.objects.filter(
        Q(id__in=assigned_request_ids) |
        Q(id__in=pending_requests.values_list('id', flat=True))
    ).distinct().select_related('required_skill', 'customer')
    
    pending_count = pending_requests.count()
    all_requests_count = all_requests_today.count()
    
    active_technicians = Technician.objects.filter(
        is_active=True, 
        depot_lat__isnull=False, 
        depot_lon__isnull=False
    ).prefetch_related('skills', 'user')
    
    active_tech_count = active_technicians.count()
    
    # Get technician availability info for the filter date
    # Check assignments on filter_date and the day before/after for context
    filter_date_prev = filter_date - timedelta(days=1)
    filter_date_next = filter_date + timedelta(days=1)
    
    # Get assignments for the filter date
    filter_date_assignments = Assignment.objects.filter(
        assigned_date=filter_date,
        status__in=['assigned', 'in_progress', 'completed'],
        technician__in=active_technicians
    ).select_related('technician', 'service_request', 'service_request__customer')
    
    # Group assignments by technician ID for the filter date
    assignments_by_tech = {}
    for assign in filter_date_assignments:
        tech_id = assign.technician.id
        if tech_id not in assignments_by_tech:
            assignments_by_tech[tech_id] = []
        assignments_by_tech[tech_id].append(assign)
    
    # Also get previous day assignments to show context
    prev_day_assignments = Assignment.objects.filter(
        assigned_date=filter_date_prev,
        status__in=['assigned', 'in_progress'],
        technician__in=active_technicians
    ).select_related('technician')
    
    prev_day_by_tech = {}
    for assign in prev_day_assignments:
        tech_id = assign.technician.id
        if tech_id not in prev_day_by_tech:
            prev_day_by_tech[tech_id] = []
        prev_day_by_tech[tech_id].append(assign)
    
    today = timezone.now().date()
    
    # Build technician data based on filter date (skills already prefetched)
    technicians_data = []
    for tech in active_technicians:
        skills_list = [skill.name for skill in tech.skills.all()]  # Already prefetched
        
        # Get assignments for the filter date
        tech_filter_date_assignments = assignments_by_tech.get(tech.id, [])
        tech_filter_date_count = len(tech_filter_date_assignments)
        
        # Get assignments for previous day for context
        tech_prev_day_count = len(prev_day_by_tech.get(tech.id, []))
        
        # Calculate available capacity
        used_minutes = sum(a.service_request.service_minutes for a in tech_filter_date_assignments if a.service_request)
        available_minutes = max(0, tech.capacity_minutes - used_minutes)
        
        technicians_data.append({
            'technician': tech,
            'username': tech.user.username,
            'skills': skills_list,
            'shift': f"{tech.shift_start.strftime('%H:%M')} - {tech.shift_end.strftime('%H:%M')}",
            'capacity': f"{tech.capacity_minutes // 60}h {tech.capacity_minutes % 60}m",
            'filter_date_assignments': tech_filter_date_count,
            'filter_date_assignment_list': tech_filter_date_assignments,  # List of actual assignments
            'prev_day_assignments': tech_prev_day_count,
            'is_available': tech_filter_date_count == 0,
            'available_capacity_minutes': available_minutes,
            'available_capacity': f"{available_minutes // 60}h {available_minutes % 60}m",
            'used_capacity': f"{used_minutes // 60}h {used_minutes % 60}m",
        })
    
    # Get all requests for the date (pending + assigned)
    all_requests_data = []
    pending_requests_data = []
    assigned_requests_data = []
    
    # Get assignments for this date to map to requests
    assignments_by_request_id = {}
    for assign in filter_date_assignments:
        req_id = assign.service_request_id
        if req_id not in assignments_by_request_id:
            assignments_by_request_id[req_id] = []
        assignments_by_request_id[req_id].append(assign)
    
    for req in all_requests_today:
        required_skill = req.required_skill.name if req.required_skill else 'No skill required'
        window_date = req.window_start.date() if req.window_start else None
        
        request_data = {
            'request': req,
            'name': req.name,
            'customer': req.customer.username,
            'required_skill': required_skill,
            'window_date': window_date,
            'window_start': req.window_start.strftime('%Y-%m-%d %H:%M') if req.window_start else 'N/A',
            'window_end': req.window_end.strftime('%Y-%m-%d %H:%M') if req.window_end else 'N/A',
            'priority': req.get_priority_display() if hasattr(req, 'get_priority_display') else req.priority,
            'status': req.status,
            'assignments': assignments_by_request_id.get(req.id, []),
        }
        
        all_requests_data.append(request_data)
        
        if req.status == 'pending':
            pending_requests_data.append(request_data)
        elif req.id in assigned_request_ids:
            assigned_requests_data.append(request_data)
    
    # Travel time analysis for pending requests
    from maps.services import DistanceService
    
    travel_time_analysis = {
        'avg_speed_kph': config.avg_speed_kph if config else 40,
        'issues': [],
        'sample_distances': [],
        'max_distance': 0,
        'avg_distance': 0,
        'max_travel_minutes': 0,
    }
    
    if pending_requests.exists() and active_technicians.exists():
        # Calculate sample distances between locations
        distances = []
        sample_pairs = []
        
        # Check distances between requests
        valid_requests = [r for r in pending_requests if r.lat and r.lon]
        if len(valid_requests) >= 2:
            for i in range(min(5, len(valid_requests) - 1)):
                for j in range(i + 1, min(i + 2, len(valid_requests))):
                    dist_km = DistanceService.haversine_km(
                        valid_requests[i].lat, valid_requests[i].lon,
                        valid_requests[j].lat, valid_requests[j].lon
                    )
                    distances.append(dist_km)
                    sample_pairs.append({
                        'from': valid_requests[i].name,
                        'to': valid_requests[j].name,
                        'distance_km': round(dist_km, 2),
                        'travel_minutes': round((dist_km / travel_time_analysis['avg_speed_kph']) * 60, 1)
                    })
        
        # Check distances from tech depots to requests
        valid_techs = [t for t in active_technicians if t.depot_lat and t.depot_lon]
        if valid_techs and valid_requests:
            for tech in valid_techs[:3]:  # Sample first 3 techs
                for req in valid_requests[:3]:  # Sample first 3 requests
                    dist_km = DistanceService.haversine_km(
                        tech.depot_lat, tech.depot_lon,
                        req.lat, req.lon
                    )
                    distances.append(dist_km)
        
        if distances:
            travel_time_analysis['max_distance'] = max(distances)
            travel_time_analysis['avg_distance'] = sum(distances) / len(distances)
            travel_time_analysis['sample_distances'] = sample_pairs[:5]  # Top 5 samples
            
            # Analyze issues
            max_travel_minutes = (travel_time_analysis['max_distance'] / travel_time_analysis['avg_speed_kph']) * 60
            travel_time_analysis['max_travel_minutes'] = round(max_travel_minutes, 1)
            
            if max_travel_minutes > 60:
                travel_time_analysis['issues'].append({
                    'type': 'high_travel_time',
                    'severity': 'warning',
                    'message': f'Maximum travel time between nodes is {max_travel_minutes:.1f} minutes ({max_travel_minutes/60:.1f} hours)',
                    'reason': 'Locations are far apart or speed setting is too low',
                    'max_distance_km': round(travel_time_analysis['max_distance'], 2),
                    'speed_setting': travel_time_analysis['avg_speed_kph']
                })
            
            if travel_time_analysis['avg_distance'] > 20:
                travel_time_analysis['issues'].append({
                    'type': 'far_locations',
                    'severity': 'info',
                    'message': f'Average distance between locations is {travel_time_analysis["avg_distance"]:.1f} km',
                    'reason': 'Locations are spread across Melbourne area',
                })
            
            if travel_time_analysis['avg_speed_kph'] < 30:
                travel_time_analysis['issues'].append({
                    'type': 'low_speed',
                    'severity': 'suggestion',
                    'message': f'Speed setting is {travel_time_analysis["avg_speed_kph"]} km/h',
                    'reason': 'For Melbourne city driving, consider 30-50 km/h',
                })
    
    # Get all existing assignments for the filter date to show what's already assigned
    existing_assignments_data = []
    for assign in filter_date_assignments.order_by('technician', 'sequence_order'):
        existing_assignments_data.append({
            'assignment': assign,
            'technician': assign.technician.user.username if assign.technician and assign.technician.user else 'Unassigned',
            'service_request': assign.service_request.name,
            'customer': assign.service_request.customer.username if assign.service_request and assign.service_request.customer else 'N/A',
            'status': assign.get_status_display() if hasattr(assign, 'get_status_display') else assign.status,
            'planned_start': assign.planned_start.strftime('%H:%M') if assign.planned_start else 'N/A',
            'planned_finish': assign.planned_finish.strftime('%H:%M') if assign.planned_finish else 'N/A',
            'sequence_order': assign.sequence_order,
        })
    
    # Get unserved reasons from session (if any) and filter by current filter_date
    unserved_reasons_raw = request.session.get('unserved_reasons', None)
    unserved_date_str = request.session.get('unserved_date', None)
    
    unserved_reasons = None
    if unserved_reasons_raw and unserved_date_str:
        # Only show unserved reasons if they match the current filter date
        if unserved_date_str == filter_date_str:
            unserved_reasons = unserved_reasons_raw
            # Don't pop - keep it until user changes date or new assignment runs
        else:
            # Clear old unserved reasons if date doesn't match
            request.session.pop('unserved_reasons', None)
            request.session.pop('unserved_date', None)
    
    context = {
        'pending_count': pending_count,
        'all_requests_count': all_requests_count,
        'assigned_count': len(assigned_requests_data),
        'active_tech_count': active_tech_count,
        'today': timezone.now().date(),
        'filter_date': filter_date,
        'filter_date_str': filter_date.strftime('%Y-%m-%d'),
        'pending_requests': pending_requests,  # Keep for backward compatibility
        'technicians_data': technicians_data,
        'pending_requests_data': pending_requests_data,
        'all_requests_data': all_requests_data,
        'assigned_requests_data': assigned_requests_data,
        'travel_time_analysis': travel_time_analysis,
        'existing_assignments': existing_assignments_data,
        'existing_assignments_count': len(existing_assignments_data),
        'unserved_reasons': unserved_reasons,
    }
    
    return render(request, 'core/admin_assign.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_technician_view(request, technician_id=None):
    """Admin view to check technician assignments, map, and timeline"""
    from datetime import datetime, timedelta
    import json
    
    # Get filter date
    filter_date_str = request.GET.get('date', None)
    if filter_date_str:
        try:
            filter_date = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
        except:
            filter_date = timezone.now().date()
    else:
        filter_date = timezone.now().date()
    
    # Get view mode (assignments, map, timeline)
    view_mode = request.GET.get('view', 'assignments')  # assignments, map, timeline
    
    # Get all active technicians
    technicians = Technician.objects.filter(is_active=True).select_related('user').order_by('user__username')
    
    technician = None
    assignments = []
    route_data = None
    timeline_data = []
    
    if technician_id:
        try:
            technician = Technician.objects.select_related('user').get(id=technician_id, is_active=True)
            
            # Get assignments for the filter date
            assignments = Assignment.objects.filter(
                technician=technician,
                assigned_date=filter_date
            ).order_by('sequence_order').select_related('service_request', 'service_request__customer')
            
            # Build route data for map
            if assignments.exists() and view_mode == 'map':
                stops = []
                for assign in assignments:
                    if assign.service_request.lat and assign.service_request.lon:
                        stops.append({
                            'position': {'lat': assign.service_request.lat, 'lng': assign.service_request.lon},
                            'customer': assign.service_request.customer.username,
                            'address': assign.service_request.address,
                            'name': assign.service_request.name,
                            'sequence': assign.sequence_order,
                            'planned_start': assign.planned_start.strftime('%H:%M') if assign.planned_start else 'N/A',
                            'planned_finish': assign.planned_finish.strftime('%H:%M') if assign.planned_finish else 'N/A',
                            'service_duration': assign.service_request.service_minutes,
                            'status': assign.status,
                        })
                
                route_data = {
                    'depot': {
                        'lat': technician.depot_lat,
                        'lng': technician.depot_lon,
                        'address': technician.depot_address,
                    },
                    'stops': stops,
                    'stops_json': json.dumps(stops),
                }
            
            # Build timeline data
            if assignments.exists() and view_mode == 'timeline':
                for assign in assignments:
                    timeline_data.append({
                        'assignment': assign,
                        'start_time': assign.planned_start,
                        'end_time': assign.planned_finish,
                        'duration': assign.service_request.service_minutes,
                        'customer': assign.service_request.customer.username,
                        'service_name': assign.service_request.name,
                        'address': assign.service_request.address,
                        'status': assign.status,
                        'sequence': assign.sequence_order,
                    })
        
        except Technician.DoesNotExist:
            messages.error(request, 'Technician not found.')
            technician = None
    
    config = GoogleMapsConfig.load()
    
    context = {
        'technicians': technicians,
        'selected_technician': technician,
        'assignments': assignments,
        'filter_date': filter_date,
        'filter_date_str': filter_date.strftime('%Y-%m-%d'),
        'view_mode': view_mode,
        'route_data': route_data,
        'timeline_data': timeline_data,
        'api_key': config.api_key if config else '',
        'today': timezone.now().date(),
    }
    
    return render(request, 'core/admin_technician_view.html', context)


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
