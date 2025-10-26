from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from accounts.models import User
from core.models import Technician, Skill, GoogleMapsConfig
from maps.services import GeocodingService


def technician_signup_view(request):
    """Public technician signup - creates account and profile"""
    if request.user.is_authenticated:
        # If already logged in, redirect to technician profile creation
        return redirect('core:technician_signup')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone', '')
        
        depot_address = request.POST.get('depot_address')
        shift_start = request.POST.get('shift_start')
        shift_end = request.POST.get('shift_end')
        capacity_hours = request.POST.get('capacity_hours')
        color_hex = request.POST.get('color_hex', '#4285F4')
        skill_ids = request.POST.getlist('skills')
        
        # Validate passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            all_skills = Skill.objects.filter(is_active=True)
            return render(request, 'accounts/technician_signup.html', {'all_skills': all_skills})
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            all_skills = Skill.objects.filter(is_active=True)
            return render(request, 'accounts/technician_signup.html', {'all_skills': all_skills})
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            user.phone = phone
            user.role = 'TECHNICIAN'
            user.save()
            
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
                    
                    # Log in the user
                    login(request, user)
                    
                    messages.success(request, 'Technician account and profile created successfully!')
                    return redirect('core:technician_dashboard')
                else:
                    messages.error(request, 'Could not find the depot address. Please enter a valid Melbourne address.')
            except Exception as e:
                messages.error(request, f'Error geocoding address: {str(e)}')
                # Delete the user if we can't create the profile
                user.delete()
                
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    # Get all skills for the form
    all_skills = Skill.objects.filter(is_active=True)
    
    # Get Google Maps API key
    config = GoogleMapsConfig.load()
    
    context = {
        'all_skills': all_skills,
        'api_key': config.api_key if config else 'AIzaSyCZCEanL50XqkGdej2VdZUCwRrkcf1RrYw',
    }
    
    return render(request, 'accounts/technician_signup.html', context)

