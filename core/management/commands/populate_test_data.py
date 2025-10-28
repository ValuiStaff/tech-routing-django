from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import pytz
from accounts.models import User
from core.models import Skill, Technician, ServiceRequest, GoogleMapsConfig
from maps.services import GeocodingService

User = get_user_model()
geocoding = GeocodingService()


class Command(BaseCommand):
    help = 'Populate database with test data'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating Google Maps config...')
        config, _ = GoogleMapsConfig.objects.get_or_create(pk=1)
        if not config.api_key:
            config.api_key = 'YOUR_GOOGLE_MAPS_API_KEY_HERE'  # User should update this
        config.save()
        
        self.stdout.write('Creating skills...')
        skills_data = [
            ('gas', 'Gas'),
            ('electric', 'Electric'),
            ('plumbing', 'Plumbing'),
            ('hvac', 'HVAC'),
            ('carpentry', 'Carpentry'),
            ('it', 'IT'),
            ('security', 'Security'),
            ('solar', 'Solar'),
            ('roofing', 'Roofing'),
            ('cleaning', 'Cleaning'),
        ]
        
        skills = {}
        for slug, name in skills_data:
            skill, _ = Skill.objects.get_or_create(slug=slug, defaults={'name': name})
            skills[slug] = skill
        
        self.stdout.write('Creating users...')
        # Admin
        admin, _ = User.objects.get_or_create(username='admin', defaults={
            'email': 'admin@test.com',
            'role': 'ADMIN',
            'is_staff': True,
            'is_superuser': True,
        })
        admin.set_password('admin123')
        admin.save()
        
        # Technician 1
        tech1, _ = User.objects.get_or_create(username='tech1', defaults={
            'email': 'tech1@test.com',
            'role': 'TECHNICIAN',
        })
        tech1.set_password('tech123')
        tech1.save()
        
        # Technician 2
        tech2, _ = User.objects.get_or_create(username='tech2', defaults={
            'email': 'tech2@test.com',
            'role': 'TECHNICIAN',
        })
        tech2.set_password('tech123')
        tech2.save()
        
        # Customer 1
        cust1, _ = User.objects.get_or_create(username='customer1', defaults={
            'email': 'customer1@test.com',
            'role': 'CUSTOMER',
        })
        cust1.set_password('cust123')
        cust1.save()
        
        # Customer 2
        cust2, _ = User.objects.get_or_create(username='customer2', defaults={
            'email': 'customer2@test.com',
            'role': 'CUSTOMER',
        })
        cust2.set_password('cust123')
        cust2.save()
        
        self.stdout.write('Creating technicians...')
        # Technician 1 profile
        t1, _ = Technician.objects.get_or_create(user=tech1, defaults={
            'depot_address': '333 Collins St, Melbourne VIC 3000',
            'capacity_minutes': 480,
            'shift_start': datetime.strptime('08:00', '%H:%M').time(),
            'shift_end': datetime.strptime('17:00', '%H:%M').time(),
            'color_hex': '#4285F4',
        })
        
        # Geocode depot addresses
        if not t1.depot_lat:
            coord, err = geocoding.geocode(t1.depot_address)
            if coord:
                t1.depot_lat, t1.depot_lon = coord
                t1.save()
        
        t1.skills.add(skills['gas'], skills['electric'])
        
        # Technician 2 profile
        t2, _ = Technician.objects.get_or_create(user=tech2, defaults={
            'depot_address': '1 Flinders St, Melbourne VIC 3000',
            'capacity_minutes': 480,
            'shift_start': datetime.strptime('08:00', '%H:%M').time(),
            'shift_end': datetime.strptime('17:00', '%H:%M').time(),
            'color_hex': '#EA4335',
        })
        
        if not t2.depot_lat:
            coord, err = geocoding.geocode(t2.depot_address)
            if coord:
                t2.depot_lat, t2.depot_lon = coord
                t2.save()
        
        t2.skills.add(skills['plumbing'], skills['hvac'])
        
        self.stdout.write('Creating service requests...')
        today = timezone.now().date()
        
        # Customer 1 requests
        req1, _ = ServiceRequest.objects.get_or_create(
            customer=cust1,
            name='Melbourne Central Repair',
            defaults={
                'address': 'Melbourne Central, Melbourne VIC 3000',
                'service_minutes': 60,
                'window_start': timezone.make_aware(datetime.combine(today, datetime.strptime('09:00', '%H:%M').time())),
                'window_end': timezone.make_aware(datetime.combine(today, datetime.strptime('15:00', '%H:%M').time())),
                'priority': 1,
                'status': 'pending',
            }
        )
        if not req1.lat:
            coord, _ = geocoding.geocode(req1.address)
            if coord:
                req1.lat, req1.lon = coord
                req1.save()
        req1.required_skill = skills['gas']
        req1.save()
        
        # Customer 2 requests
        req2, _ = ServiceRequest.objects.get_or_create(
            customer=cust2,
            name='Queen Victoria Market Plumbing',
            defaults={
                'address': 'Queen Victoria Market, Melbourne VIC 3000',
                'service_minutes': 90,
                'window_start': timezone.make_aware(datetime.combine(today, datetime.strptime('09:00', '%H:%M').time())),
                'window_end': timezone.make_aware(datetime.combine(today, datetime.strptime('14:00', '%H:%M').time())),
                'priority': 1,
                'status': 'pending',
            }
        )
        if not req2.lat:
            coord, _ = geocoding.geocode(req2.address)
            if coord:
                req2.lat, req2.lon = coord
                req2.save()
        req2.required_skill = skills['plumbing']
        req2.save()
        
        self.stdout.write(self.style.SUCCESS('Test data created successfully!'))
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Technician 1: tech1 / tech123')
        self.stdout.write('  Technician 2: tech2 / tech123')
        self.stdout.write('  Customer 1: customer1 / cust123')
        self.stdout.write('  Customer 2: customer2 / cust123')

