from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from core.models import ServiceRequest, Assignment, Technician, GoogleMapsConfig
from maps.services import GeocodingService, haversine_km


@login_required
@user_passes_test(lambda u: u.is_customer() or u.is_superuser)
def customer_dashboard(request):
    """Customer dashboard - show their service requests"""
    customer = request.user
    
    # Get customer's service requests (most recent first)
    requests = ServiceRequest.objects.filter(customer=customer).order_by('-created_at')
    
    # Get any existing assignments for these requests
    assignments = Assignment.objects.filter(
        service_request__in=requests
    ).select_related('technician', 'service_request')
    
    # Check if customer has active request (pending or assigned or in_progress)
    active_request = ServiceRequest.objects.filter(
        customer=customer,
        status__in=['pending', 'assigned', 'in_progress']
    ).first()
    
    context = {
        'requests': requests,
        'assignments': assignments,
        'active_request': active_request,
        'can_submit_new': active_request is None,
    }
    
    return render(request, 'core/customer_dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.is_customer() or u.is_superuser)
def customer_submit_request(request):
    """Customer submit service request form"""
    customer = request.user
    
    # Check if customer already has active request
    active_request = ServiceRequest.objects.filter(
        customer=customer,
        status__in=['pending', 'assigned', 'in_progress']
    ).first()
    
    if active_request:
        messages.warning(request, 'You already have an active request. Please complete it before submitting a new one.')
        return redirect('core:customer_dashboard')
    
    if request.method == 'POST':
        from core.forms import ServiceRequestForm
        from django.contrib.auth import get_user_model
        
        form = ServiceRequestForm(request.POST)
        
        if form.is_valid():
            # Geocode the address
            address = form.cleaned_data['address']
            service_type = form.cleaned_data.get('service_type', '')
            gmaps = GeocodingService()
            
            try:
                coords, _ = gmaps.geocode(address)
                if coords:
                    lat, lon = coords
                else:
                    lat, lon = None, None
                
                if lat and lon:
                    # Create service request
                    service_request = form.save(commit=False)
                    service_request.customer = customer
                    service_request.lat = lat
                    service_request.lon = lon
                    # Set name from service type
                    if service_type:
                        service_request.name = service_type
                    service_request.save()
                    form.save_m2m()  # Save M2M relationships (required_skills)
                    
                    messages.success(request, 'Service request submitted successfully!')
                    return redirect('core:customer_dashboard')
                else:
                    messages.error(request, 'Could not find the address. Please enter a valid Melbourne address.')
            except Exception as e:
                messages.error(request, f'Error geocoding address: {str(e)}')
        else:
            # Log form errors for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Form errors: {form.errors}')
            logger.error(f'Form data: {request.POST}')
            messages.error(request, f'Please correct the form errors: {form.errors}')
    else:
        from core.forms import ServiceRequestForm
        form = ServiceRequestForm()
    
    # Get Google Maps API key for autocomplete
    config = GoogleMapsConfig.load()
    
    context = {
        'form': form,
        'api_key': config.api_key if config else '',
    }
    
    return render(request, 'core/customer_submit_request.html', context)


@login_required
@user_passes_test(lambda u: u.is_customer() or u.is_superuser)
def customer_nearby_technicians(request):
    """Show technicians who will be near customer's location"""
    customer = request.user
    
    # Get customer's latest request (if any)
    latest_request = ServiceRequest.objects.filter(customer=customer).first()
    
    if not latest_request or not latest_request.lat or not latest_request.lon:
        return JsonResponse({'error': 'No location data available'}, status=400)
    
    # Get all active assignments today
    today = timezone.now().date()
    assignments = Assignment.objects.filter(
        assigned_date=today,
        status='assigned'
    ).select_related('technician', 'service_request')
    
    # Find technicians who will be within 5km of customer's location
    nearby_technicians = []
    markers_data = []
    
    for assignment in assignments:
        # Get technician's route stops
        tech_assignments = Assignment.objects.filter(
            technician=assignment.technician,
            assigned_date=today,
            status='assigned'
        ).select_related('service_request', 'technician')
        
        # Calculate distance to each stop
        for assign in tech_assignments:
            distance = haversine_km(
                latest_request.lat, latest_request.lon,
                assign.service_request.lat, assign.service_request.lon
            )
            
            if distance <= 5.0:  # Within 5km
                nearby_technicians.append({
                    'technician': assignment.technician.user.username,
                    'customer': assign.service_request.name,
                    'address': assign.service_request.address,
                    'distance_km': round(distance, 2),
                    'arrival_time': assign.planned_start.strftime('%H:%M'),
                    'sequence': assign.sequence_order,
                })
                
                # Add marker data for map
                markers_data.append({
                    'position': {'lat': assign.service_request.lat, 'lng': assign.service_request.lon},
                    'title': f"{assignment.technician.user.username} - {assign.service_request.name}",
                    'label': assignment.technician.user.username[0].upper(),
                    'info': f"{assign.service_request.name}<br>{assign.service_request.address}<br>Arrival: {assign.planned_start.strftime('%H:%M')}",
                    'distance': round(distance, 2),
                })
                break  # Only show each technician once
    
    # Remove duplicates
    seen = set()
    unique_nearby = []
    for tech in nearby_technicians:
        key = tech['technician']
        if key not in seen:
            seen.add(key)
            unique_nearby.append(tech)
    
    config = GoogleMapsConfig.load()
    
    context = {
        'customer_location': {
            'address': latest_request.address,
            'lat': latest_request.lat,
            'lon': latest_request.lon,
        },
        'nearby_technicians': unique_nearby,
        'markers': markers_data,
        'api_key': config.api_key if config else '',
    }
    
    return render(request, 'core/customer_nearby_technicians.html', context)

