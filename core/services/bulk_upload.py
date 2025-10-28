"""
Bulk Upload Service for processing Excel files with customer and technician data
"""
import pandas as pd
from datetime import datetime, date, time
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from core.models import Technician, ServiceRequest, Skill, GoogleMapsConfig
from maps.services import GeocodingService

User = get_user_model()


class BulkUploadService:
    """Process bulk user upload from Excel file"""
    
    def __init__(self):
        self.results = {
            'created_users': [],
            'updated_users': [],
            'created_requests': [],
            'created_technicians': [],
            'errors': [],
            'warnings': []
        }
        self.geocoding_service = GeocodingService()
    
    def process_excel_file(self, file):
        """
        Process uploaded Excel file and create users, service requests, and technicians
        
        Args:
            file: Django uploaded file object (Excel)
            
        Returns:
            dict: Results with created/updated records and errors
        """
        try:
            # Read Excel file
            df = pd.read_excel(file)
            
            # Validate required columns
            required_columns = ['Type', 'Username', 'Email']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                self.results['errors'].append(
                    f"Missing required columns: {', '.join(missing_columns)}"
                )
                return self.results
            
            # Process each row
            for idx, row in df.iterrows():
                try:
                    user_type = str(row.get('Type', '')).strip().upper()
                    
                    if user_type == 'CUSTOMER':
                        self._process_customer(row, idx + 2)  # +2 for Excel row number
                    elif user_type == 'TECHNICIAN':
                        self._process_technician(row, idx + 2)
                    else:
                        self.results['errors'].append(
                            f"Row {idx + 2}: Invalid Type '{user_type}'. Must be 'Customer' or 'Technician'"
                        )
                        
                except Exception as e:
                    self.results['errors'].append(
                        f"Row {idx + 2}: {str(e)}"
                    )
            
            return self.results
            
        except Exception as e:
            self.results['errors'].append(f"Error reading Excel file: {str(e)}")
            return self.results
    
    def _process_customer(self, row, row_num):
        """Process a customer row from Excel"""
        username = str(row.get('Username', '')).strip()
        email = str(row.get('Email', '')).strip()
        
        if not username or not email:
            self.results['errors'].append(f"Row {row_num}: Username and Email are required")
            return
        
        # Get or create user
        user, created = self._get_or_create_user(row, row_num, 'CUSTOMER')
        if not user:
            return
        
        if created:
            self.results['created_users'].append(user)
        else:
            self.results['updated_users'].append(user)
        
        # Create service request if customer data provided
        address = row.get('Address', '').strip()
        if address:
            try:
                # Geocode address and validate Melbourne
                coords = self._geocode_address(address, row_num)
                if not coords:
                    return
                
                lat, lon = coords
                
                # Parse service request data
                service_minutes = int(row.get('ServiceMinutes', 60)) if pd.notna(row.get('ServiceMinutes')) else 60
                
                window_start = self._parse_datetime(row.get('WindowStart'), row_num)
                window_end = self._parse_datetime(row.get('WindowEnd'), row_num)
                
                if not window_start or not window_end:
                    return
                
                # Parse priority
                priority_str = str(row.get('Priority', '')).strip().lower()
                priority_map = {'high': 1, 'medium': 2, 'low': 3}
                priority = priority_map.get(priority_str, 2)
                
                # Create service request
                service_request = ServiceRequest.objects.create(
                    customer=user,
                    name=str(row.get('ServiceType', 'Service Request')).strip(),
                    address=address,
                    lat=lat,
                    lon=lon,
                    service_minutes=service_minutes,
                    window_start=window_start,
                    window_end=window_end,
                    priority=priority,
                    status='pending'
                )
                
                # Add required skills
                skills_str = str(row.get('RequiredSkills', '')).strip()
                if skills_str:
                    self._add_skills_to_service_request(service_request, skills_str, row_num)
                
                self.results['created_requests'].append(service_request)
                
            except Exception as e:
                self.results['errors'].append(f"Row {row_num}: Error creating service request: {str(e)}")
    
    def _process_technician(self, row, row_num):
        """Process a technician row from Excel"""
        username = str(row.get('Username', '')).strip()
        email = str(row.get('Email', '')).strip()
        
        if not username or not email:
            self.results['errors'].append(f"Row {row_num}: Username and Email are required")
            return
        
        # Get or create user
        user, created = self._get_or_create_user(row, row_num, 'TECHNICIAN')
        if not user:
            return
        
        if created:
            self.results['created_users'].append(user)
        else:
            self.results['updated_users'].append(user)
        
        # Create or update technician profile
        depot_address = str(row.get('DepotAddress', '')).strip()
        if not depot_address:
            self.results['errors'].append(f"Row {row_num}: DepotAddress is required for technicians")
            return
        
        try:
            # Geocode depot address and validate Melbourne
            coords = self._geocode_address(depot_address, row_num)
            if not coords:
                return
            
            depot_lat, depot_lon = coords
            
            # Parse capacity
            capacity_hours = row.get('CapacityHours', 8)
            if pd.notna(capacity_hours):
                capacity_minutes = int(float(capacity_hours) * 60)
            else:
                capacity_minutes = 480
            
            # Parse shift times
            shift_start = self._parse_time(row.get('ShiftStart'), row_num)
            shift_end = self._parse_time(row.get('ShiftEnd'), row_num)
            
            if not shift_start or not shift_end:
                return
            
            # Get or create technician profile
            technician, tech_created = Technician.objects.get_or_create(
                user=user,
                defaults={
                    'depot_address': depot_address,
                    'depot_lat': depot_lat,
                    'depot_lon': depot_lon,
                    'capacity_minutes': capacity_minutes,
                    'shift_start': shift_start,
                    'shift_end': shift_end,
                    'color_hex': str(row.get('ColorHex', '#4285F4')).strip(),
                    'is_active': True
                }
            )
            
            if not tech_created:
                # Update existing technician
                technician.depot_address = depot_address
                technician.depot_lat = depot_lat
                technician.depot_lon = depot_lon
                technician.capacity_minutes = capacity_minutes
                technician.shift_start = shift_start
                technician.shift_end = shift_end
                technician.color_hex = str(row.get('ColorHex', '#4285F4')).strip()
                technician.save()
            
            # Add skills
            skills_str = str(row.get('Skills', '')).strip()
            if skills_str:
                self._add_skills_to_technician(technician, skills_str, row_num)
            
            if tech_created:
                self.results['created_technicians'].append(technician)
            else:
                self.results['updated_users'].append(user)
            
        except Exception as e:
            self.results['errors'].append(f"Row {row_num}: Error creating technician: {str(e)}")
    
    def _get_or_create_user(self, row, row_num, role):
        """Get or create user with password handling"""
        username = str(row.get('Username', '')).strip()
        email = str(row.get('Email', '')).strip()
        password = str(row.get('Password', 'Welcome123')).strip()
        
        if not username or not email:
            return None, False
        
        # Get existing user or create new
        user = User.objects.filter(username=username).first()
        created = False
        
        if user:
            # Update existing user
            user.email = email
            user.role = role
            user.plaintext_password = password  # Store plaintext password
            user.set_password(password)  # Set hashed password
            user.save()
        else:
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role
            )
            user.plaintext_password = password  # Store plaintext password
            user.save()
            created = True
        
        return user, created
    
    def _geocode_address(self, address, row_num):
        """Geocode address and validate Melbourne location"""
        try:
            coords, full_address = self.geocoding_service.geocode(address)
            
            if not coords:
                self.results['errors'].append(f"Row {row_num}: Could not geocode address: {address}")
                return None
            
            lat, lon = coords
            
            # Check if address is in Melbourne
            if not self._is_melbourne_address(full_address):
                self.results['errors'].append(
                    f"Row {row_num}: Address '{address}' is not in Melbourne. Full address: {full_address}"
                )
                return None
            
            return (lat, lon)
            
        except Exception as e:
            self.results['errors'].append(f"Row {row_num}: Geocoding error: {str(e)}")
            return None
    
    def _is_melbourne_address(self, full_address):
        """Check if address is in Melbourne area"""
        address_lower = full_address.lower()
        melbourne_indicators = ['melbourne', 'vic', 'victoria']
        return any(indicator in address_lower for indicator in melbourne_indicators)
    
    def _parse_datetime(self, value, row_num):
        """Parse datetime string to DateTime object"""
        if pd.isna(value):
            return None
        
        try:
            # Try various datetime formats
            if isinstance(value, str):
                # Try common formats
                for fmt in ['%Y-%m-%d %H:%M', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M', '%d-%m-%Y %H:%M']:
                    try:
                        return datetime.strptime(value.strip(), fmt)
                    except ValueError:
                        continue
            elif isinstance(value, pd.Timestamp):
                return value.to_pydatetime()
            elif isinstance(value, datetime):
                return value
            
            self.results['errors'].append(f"Row {row_num}: Could not parse datetime: {value}")
            return None
            
        except Exception as e:
            self.results['errors'].append(f"Row {row_num}: Datetime parse error: {str(e)}")
            return None
    
    def _parse_time(self, value, row_num):
        """Parse time string to Time object"""
        if pd.isna(value):
            return None
        
        try:
            if isinstance(value, str):
                # Try common time formats
                for fmt in ['%H:%M', '%H:%M:%S', '%I:%M %p', '%I:%M:%S %p']:
                    try:
                        dt = datetime.strptime(value.strip(), fmt)
                        return dt.time()
                    except ValueError:
                        continue
            elif isinstance(value, time):
                return value
            elif isinstance(value, pd.Timestamp):
                return value.time()
            
            self.results['errors'].append(f"Row {row_num}: Could not parse time: {value}")
            return None
            
        except Exception as e:
            self.results['errors'].append(f"Row {row_num}: Time parse error: {str(e)}")
            return None
    
    def _add_skills_to_service_request(self, service_request, skills_str, row_num):
        """Add skills to service request"""
        skill_names = [s.strip() for s in skills_str.split(',') if s.strip()]
        
        for skill_name in skill_names:
            skill = Skill.objects.filter(name__iexact=skill_name, is_active=True).first()
            if skill:
                service_request.required_skills.add(skill)
            else:
                self.results['warnings'].append(
                    f"Row {row_num}: Skill '{skill_name}' not found. Creating new skill."
                )
                skill = Skill.objects.create(name=skill_name, is_active=True)
                service_request.required_skills.add(skill)
    
    def _add_skills_to_technician(self, technician, skills_str, row_num):
        """Add skills to technician"""
        skill_names = [s.strip() for s in skills_str.split(',') if s.strip()]
        
        for skill_name in skill_names:
            skill = Skill.objects.filter(name__iexact=skill_name, is_active=True).first()
            if skill:
                technician.skills.add(skill)
            else:
                self.results['warnings'].append(
                    f"Row {row_num}: Skill '{skill_name}' not found. Creating new skill."
                )
                skill = Skill.objects.create(name=skill_name, is_active=True)
                technician.skills.add(skill)
    
    def process_manual_entries(self, post_data):
        """Process manual entry data from form submission"""
        row_count = 0
        processed = 0
        
        # Find all entries (rows) by counting unique type fields
        while True:
            type_key = f'type_{row_count}'
            if type_key not in post_data:
                break
            
            user_type = post_data.get(type_key, '').strip().upper()
            if not user_type:
                row_count += 1
                continue
            
            username = post_data.get(f'username_{row_count}', '').strip()
            email = post_data.get(f'email_{row_count}', '').strip()
            password = post_data.get(f'password_{row_count}', 'Welcome123').strip()
            phone = post_data.get(f'phone_{row_count}', '').strip()
            
            if not username or not email:
                self.results['errors'].append(f"Row {row_count + 1}: Username and Email are required")
                row_count += 1
                processed += 1
                continue
            
            try:
                # Create or update user
                user, created = self._get_or_create_user_manual(username, email, password, phone, user_type)
                
                if not user:
                    self.results['errors'].append(f"Row {row_count + 1}: Could not create user")
                    row_count += 1
                    processed += 1
                    continue
                
                if created:
                    self.results['created_users'].append(user)
                else:
                    self.results['updated_users'].append(user)
                
                # Process customer specific fields
                if user_type == 'CUSTOMER':
                    address = post_data.get(f'address_{row_count}', '').strip()
                    service_type = post_data.get(f'service_type_{row_count}', '').strip()
                    service_minutes = post_data.get(f'service_minutes_{row_count}', '60')
                    window_start = post_data.get(f'window_start_{row_count}', '').strip()
                    window_end = post_data.get(f'window_end_{row_count}', '').strip()
                    required_skills = post_data.get(f'required_skills_{row_count}', '').strip()
                    priority = post_data.get(f'priority_{row_count}', 'medium').strip()
                    notes = post_data.get(f'notes_{row_count}', '').strip()
                    
                    if address:
                        # Create service request
                        try:
                            coords = self._geocode_address(address, row_count + 1)
                            if coords:
                                lat, lon = coords
                                
                                # Parse datetime fields
                                window_start_dt = self._parse_datetime_manual(window_start, row_count + 1)
                                window_end_dt = self._parse_datetime_manual(window_end, row_count + 1)
                                
                                if window_start_dt and window_end_dt:
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
                                    
                                    # Add required skills
                                    if required_skills:
                                        self._add_skills_to_service_request(service_request, required_skills, row_count + 1)
                                    
                                    self.results['created_requests'].append(service_request)
                        except Exception as e:
                            self.results['errors'].append(f"Row {row_count + 1}: Error creating service request: {str(e)}")
                
                # Process technician specific fields
                elif user_type == 'TECHNICIAN':
                    depot_address = post_data.get(f'depot_address_{row_count}', '').strip()
                    capacity_hours = post_data.get(f'capacity_hours_{row_count}', '8')
                    shift_start = post_data.get(f'shift_start_{row_count}', '').strip()
                    shift_end = post_data.get(f'shift_end_{row_count}', '').strip()
                    skills = post_data.get(f'skills_{row_count}', '').strip()
                    color_hex = post_data.get(f'color_hex_{row_count}', '#4285F4').strip()
                    
                    if not depot_address:
                        self.results['errors'].append(f"Row {row_count + 1}: DepotAddress is required for technicians")
                        row_count += 1
                        processed += 1
                        continue
                    
                    try:
                        coords = self._geocode_address(depot_address, row_count + 1)
                        if not coords:
                            row_count += 1
                            processed += 1
                            continue
                        
                        depot_lat, depot_lon = coords
                        capacity_minutes = int(float(capacity_hours) * 60)
                        
                        # Parse time fields
                        shift_start_time = self._parse_time_manual(shift_start, row_count + 1)
                        shift_end_time = self._parse_time_manual(shift_end, row_count + 1)
                        
                        if not shift_start_time or not shift_end_time:
                            row_count += 1
                            processed += 1
                            continue
                        
                        # Create or update technician profile
                        technician, tech_created = Technician.objects.get_or_create(
                            user=user,
                            defaults={
                                'depot_address': depot_address,
                                'depot_lat': depot_lat,
                                'depot_lon': depot_lon,
                                'capacity_minutes': capacity_minutes,
                                'shift_start': shift_start_time,
                                'shift_end': shift_end_time,
                                'color_hex': color_hex,
                                'is_active': True
                            }
                        )
                        
                        if not tech_created:
                            # Update existing
                            technician.depot_address = depot_address
                            technician.depot_lat = depot_lat
                            technician.depot_lon = depot_lon
                            technician.capacity_minutes = capacity_minutes
                            technician.shift_start = shift_start_time
                            technician.shift_end = shift_end_time
                            technician.color_hex = color_hex
                            technician.save()
                        
                        # Add skills
                        if skills:
                            self._add_skills_to_technician(technician, skills, row_count + 1)
                        
                        if tech_created:
                            self.results['created_technicians'].append(technician)
                        
                    except Exception as e:
                        self.results['errors'].append(f"Row {row_count + 1}: Error creating technician: {str(e)}")
                
                row_count += 1
                processed += 1
                
            except Exception as e:
                self.results['errors'].append(f"Row {row_count + 1}: {str(e)}")
                row_count += 1
                processed += 1
        
        return self.results
    
    def _get_or_create_user_manual(self, username, email, password, phone, role):
        """Get or create user with password handling for manual entry"""
        user = User.objects.filter(username=username).first()
        created = False
        
        if user:
            # Update existing user
            user.email = email
            user.role = role
            user.phone = phone
            user.plaintext_password = password
            user.set_password(password)
            user.save()
        else:
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role
            )
            user.phone = phone
            user.plaintext_password = password
            user.save()
            created = True
        
        return user, created
    
    def _parse_datetime_manual(self, value, row_num):
        """Parse datetime string from manual entry form"""
        if not value:
            return None
        
        try:
            # Handle datetime-local format
            if 'T' in value:
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            else:
                return datetime.strptime(value, '%Y-%m-%d %H:%M')
        except ValueError as e:
            self.results['errors'].append(f"Row {row_num}: Could not parse datetime '{value}': {str(e)}")
            return None
    
    def _parse_time_manual(self, value, row_num):
        """Parse time string from manual entry form"""
        if not value:
            return None
        
        try:
            return datetime.strptime(value, '%H:%M').time()
        except ValueError:
            self.results['errors'].append(f"Row {row_num}: Could not parse time '{value}'")
            return None

