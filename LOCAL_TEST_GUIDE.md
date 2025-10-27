# Local Testing Guide - Tech Routing Application

## Quick Start

Your application is now running locally at:
**http://localhost:8000**

## Test the Application

### 1. Access the Application
Open your browser and go to: **http://localhost:8000**

You should see:
- Home page with login/register options
- "Become a Technician" and "Register as Customer" links

### 2. Health Check
Visit: **http://localhost:8000/health/**

Expected response:
```json
{"status": "ok", "service": "tech-routing"}
```

## Create Test Users

### Start Django Shell
```bash
cd "/Users/staffuser/Desktop/App Generation /django"
source venv/bin/activate
python manage.py shell
```

### Create Admin User
```python
from accounts.models import User

# Create admin
admin = User.objects.create_user(
    username='admin',
    email='admin@test.com',
    password='admin123',
    role='ADMIN'
)
print("Admin created: admin / admin123")
```

### Create Technician
```python
from accounts.models import User
from core.models import Technician, Skill
from datetime import time

# Create technician user
tech1 = User.objects.create_user(
    username='tech1',
    email='tech1@test.com',
    password='tech123',
    role='TECHNICIAN'
)

# Create technician profile
tech_prof = Technician.objects.create(
    user=tech1,
    depot_address='333 Collins St, Melbourne VIC',
    depot_lat=-37.8153,
    depot_lon=144.9582,
    capacity_minutes=480,
    shift_start=time(8, 0),
    shift_end=time(17, 0),
    color_hex='#4285F4',
    is_active=True
)

# Add skills
gas_skill = Skill.objects.first()  # Get first skill
tech_prof.skills.add(gas_skill)
print("Technician created: tech1 / tech123")
```

### Create Customer
```python
from accounts.models import User

customer1 = User.objects.create_user(
    username='customer1',
    email='customer1@test.com',
    password='cust123',
    role='CUSTOMER'
)
print("Customer created: customer1 / cust123")
exit()
```

## Test User Flows

### 1. Test as Admin
- **Login**: admin / admin123
- Go to: http://localhost:8000/admin/
- Configure Google Maps API key
- Add skills
- View assignments

### 2. Test as Customer
- **Login**: customer1 / cust123
- Go to: http://localhost:8000/core/customer/dashboard/
- Submit a new service request
- View service request details
- Check nearby technicians

### 3. Test as Technician
- **Login**: tech1 / tech123
- Go to: http://localhost:8000/core/technician/dashboard/
- View assigned jobs
- See route map
- Update job status

## Test Features

### ✅ Health Check Endpoint
```bash
curl http://localhost:8000/health/
```

### ✅ Static Files
Visit: http://localhost:8000/static/css/ (if exists)

### ✅ Admin Panel
Visit: http://localhost:8000/admin/

### ✅ CSRF Protection
All forms should have CSRF tokens

### ✅ Authentication
Test login/logout for each role

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running, or run:
```bash
lsof -ti:8000 | xargs kill -9
```

## Next Steps

Once local testing passes:
1. ✅ Health check works
2. ✅ All pages load
3. ✅ Login works
4. ✅ Forms submit correctly
5. ✅ Database queries work

Then deploy to Koyeb:
- Follow: `KOYEB_QUICK_START.md`
- All code is already on GitHub
- Ready to deploy!

## Troubleshooting

### Port 8000 Already in Use
```bash
lsof -ti:8000 | xargs kill -9
python manage.py runserver
```

### Database Errors
```bash
python manage.py migrate
```

### Static Files Not Loading
```bash
python manage.py collectstatic
```

### Import Errors
```bash
source venv/bin/activate
pip install -r requirements.txt
```

