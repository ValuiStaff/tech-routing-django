# Django Multi-Role Technician Routing Application

A Django web application for technician scheduling and routing with OR-Tools optimization and Google Maps integration.

## Features

- **3 Role System**: Customer, Technician, and Admin roles
- **Job Assignment**: OR-Tools algorithm for optimal technician assignment
- **Google Maps Integration**: Geocoding, directions, and route visualization
- **Skills Matching**: Technicians matched to jobs based on skills
- **Time Windows**: Soft constraints with lateness penalties
- **Capacity Constraints**: Manage technician daily capacity

## Setup

1. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. Set your Google Maps API key:
```bash
python manage.py shell
>>> from core.models import GoogleMapsConfig
>>> config = GoogleMapsConfig.load()
>>> config.api_key = 'YOUR_API_KEY_HERE'
>>> config.save()
```

4. **Run migrations:**
```bash
python manage.py migrate
```

5. **Create test data:**
```bash
python manage.py populate_test_data
```

6. **Run the server:**
```bash
python manage.py runserver
```

## Test Accounts

- **Admin**: admin / admin123
- **Technician 1**: tech1 / tech123 (Skills: gas, electric)
- **Technician 2**: tech2 / tech123 (Skills: plumbing, hvac)
- **Customer 1**: customer1 / cust123
- **Customer 2**: customer2 / cust123

## Usage

### Admin Role
- Access Django admin at `/admin/`
- Manage technicians, service requests, and assignments
- Configure Google Maps settings
- View assignment interface (to be implemented)

### Customer Role
- Register new accounts
- Submit service requests
- View request status and assignments

### Technician Role
- View assigned jobs
- Update job status
- View route maps

## Architecture

- **accounts**: User authentication**
- **core**: Technicians, ServiceRequests, Assignments, Skills
- **routing**: OR-Tools solver service
- **maps**: Google Maps integration (geocoding, directions)

## Next Steps

The application currently has the foundation with:
- Database models
- Authentication system
- Django admin interface
- Google Maps services
- OR-Tools routing service

Next steps:
- Build custom customer/technician/admin dashboards
- Implement assignment interface with map visualization
- Add polyline rendering for routes
- Complete role-based access control

## Technologies

- Django 5.2
- OR-Tools (Google's optimization library)
- Google Maps API
- Bootstrap 5
- SQLite database

