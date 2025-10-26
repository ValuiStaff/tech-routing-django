from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from core.models import Technician, Assignment, Skill, ServiceRequest, GoogleMapsConfig
from maps.services import GeocodingService


@login_required
@user_passes_test(lambda u: u.is_technician() or u.is_superuser)
def technician_dashboard(request):
    """Technician dashboard - show assigned jobs"""
    try:
        technician = Technician.objects.get(user=request.user)
    except Technician.DoesNotExist:
        messages.error(request, 'Please set up your technician profile.')
        return redirect('core:technician_profile')
    
    # Get selected date (default to today)
    selected_date = request.GET.get('date', str(timezone.now().date()))
    
    try:
        from datetime import datetime
        assigned_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except:
        assigned_date = timezone.now().date()
    
    # Get technician's assignments for the selected date
    assignments = Assignment.objects.filter(
        technician=technician,
        assigned_date=assigned_date
    ).order_by('sequence_order').select_related('service_request')
    
    context = {
        'technician': technician,
        'assignments': assignments,
        'selected_date': assigned_date,
        'today': timezone.now().date(),
    }
    
    return render(request, 'core/technician_dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.is_technician() or u.is_superuser)
def technician_route_map(request):
    """Technician's route on map"""
    try:
        technician = Technician.objects.get(user=request.user)
    except Technician.DoesNotExist:
        messages.error(request, 'Please set up your technician profile.')
        return redirect('core:technician_profile')
    
    # Get selected date
    selected_date = request.GET.get('date', str(timezone.now().date()))
    
    try:
        from datetime import datetime
        assigned_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except:
        assigned_date = timezone.now().date()
    
    # Get technician's assignments
    assignments = Assignment.objects.filter(
        technician=technician,
        assigned_date=assigned_date
    ).order_by('sequence_order').select_related('service_request')
    
    # Build route data for map
    import json
    stops = []
    for assign in assignments:
        stops.append({
            'position': {'lat': assign.service_request.lat, 'lng': assign.service_request.lon},
            'customer': assign.service_request.name,
            'address': assign.service_request.address,
            'sequence': assign.sequence_order,
            'planned_start': assign.planned_start.strftime('%H:%M'),
            'service_duration': assign.service_request.service_minutes,
        })
    
    config = GoogleMapsConfig.load()
    
    context = {
        'technician': technician,
        'depot': {
            'lat': technician.depot_lat,
            'lng': technician.depot_lon,
            'address': technician.depot_address,
        },
        'stops': stops,
        'stops_json': json.dumps(stops),
        'selected_date': assigned_date,
        'api_key': config.api_key if config else '',
    }
    
    return render(request, 'core/technician_route_map.html', context)


@login_required
@user_passes_test(lambda u: u.is_technician() or u.is_superuser)
def technician_profile(request):
    """Technician profile - update availability and skills"""
    try:
        technician = Technician.objects.get(user=request.user)
    except Technician.DoesNotExist:
        messages.error(request, 'Please create your technician profile.')
        return redirect('core:technician_signup')
    
    if request.method == 'POST':
        # Update availability
        shift_start = request.POST.get('shift_start')
        shift_end = request.POST.get('shift_end')
        capacity_hours = request.POST.get('capacity_hours')
        
        if shift_start and shift_end and capacity_hours:
            from datetime import datetime, time
            try:
                # Parse times
                technician.shift_start = datetime.strptime(shift_start, '%H:%M').time()
                technician.shift_end = datetime.strptime(shift_end, '%H:%M').time()
                technician.capacity_minutes = int(capacity_hours) * 60
                technician.save()
                
                messages.success(request, 'Availability updated successfully!')
            except ValueError as e:
                messages.error(request, f'Invalid time format: {str(e)}')
        
        # Update skills
        skill_ids = request.POST.getlist('skills')
        technician.skills.set(skill_ids)
        
        messages.success(request, 'Skills updated successfully!')
        return redirect('core:technician_profile')
    
    # Get all skills
    all_skills = Skill.objects.filter(is_active=True)
    
    context = {
        'technician': technician,
        'all_skills': all_skills,
    }
    
    return render(request, 'core/technician_profile.html', context)


@login_required
def technician_signup(request):
    """Technician signup - create technician profile"""
    user = request.user
    
    # Check if already has profile
    if Technician.objects.filter(user=user).exists():
        messages.info(request, 'You already have a technician profile.')
        return redirect('core:technician_profile')
    
    if request.method == 'POST':
        depot_address = request.POST.get('depot_address')
        shift_start = request.POST.get('shift_start')
        shift_end = request.POST.get('shift_end')
        capacity_hours = request.POST.get('capacity_hours')
        color_hex = request.POST.get('color_hex', '#4285F4')
        skill_ids = request.POST.getlist('skills')
        
        if not all([depot_address, shift_start, shift_end, capacity_hours]):
            messages.error(request, 'Please fill all required fields.')
        else:
            # Geocode depot address
            gmaps = GeocodingService()
            
            try:
                coords, _ = gmaps.geocode(depot_address)
                if coords:
                    lat, lon = coords
                else:
                    lat, lon = None, None
                
                if lat and lon:
                    from datetime import datetime
                    
                    # Create technician profile
                    technician = Technician.objects.create(
                        user=user,
                        depot_address=depot_address,
                        depot_lat=lat,
                        depot_lon=lon,
                        shift_start=datetime.strptime(shift_start, '%H:%M').time(),
                        shift_end=datetime.strptime(shift_end, '%H:%M').time(),
                        capacity_minutes=int(capacity_hours) * 60,
                        color_hex=color_hex,
                        is_active=True,
                    )
                    
                    # Set skills
                    technician.skills.set(skill_ids)
                    
                    # Update user role to TECHNICIAN if not already
                    if user.role != 'TECHNICIAN':
                        user.role = 'TECHNICIAN'
                        user.save()
                    
                    messages.success(request, 'Technician profile created successfully!')
                    return redirect('core:technician_dashboard')
                else:
                    messages.error(request, 'Could not find the depot address. Please enter a valid Melbourne address.')
            except Exception as e:
                messages.error(request, f'Error creating profile: {str(e)}')
    
    # Get all skills
    all_skills = Skill.objects.filter(is_active=True)
    
    context = {
        'all_skills': all_skills,
    }
    
    return render(request, 'core/technician_signup.html', context)


@login_required
@user_passes_test(lambda u: u.is_technician() or u.is_superuser)
def technician_update_status(request, assignment_id):
    """Technician update job status (in_progress, completed)"""
    try:
        technician = Technician.objects.get(user=request.user)
        assignment = Assignment.objects.get(
            id=assignment_id,
            technician=technician
        )
    except Assignment.DoesNotExist:
        messages.error(request, 'Assignment not found.')
        return redirect('core:technician_dashboard')
    
    if request.method == 'POST':
        status = request.POST.get('status')
        
        if status in ['in_progress', 'completed']:
            assignment.status = status
            
            if status == 'in_progress':
                assignment.actual_start = timezone.now()
            elif status == 'completed':
                assignment.actual_finish = timezone.now()
            
            assignment.save()
            
            # Update service request status
            assignment.service_request.status = status
            assignment.service_request.save()
            
            messages.success(request, f'Job status updated to {status}.')
            return redirect('core:technician_dashboard')
    
    context = {
        'assignment': assignment,
    }
    
    return render(request, 'core/technician_update_status.html', context)

