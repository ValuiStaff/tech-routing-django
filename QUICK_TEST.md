# Quick Test - Your App is Running!

## Server Status
✅ **Running at**: http://localhost:8000
✅ **Health Check**: http://localhost:8000/health/

## Quick Test Commands

### Test Health Endpoint
```bash
curl http://localhost:8000/health/
```

### Check Server Status
```bash
curl -I http://localhost:8000/
```

### View Homepage
Open browser: **http://localhost:8000**

## Test Account Creation

Run in terminal:
```bash
cd "/Users/staffuser/Desktop/App Generation /django"
source venv/bin/activate
python manage.py shell
```

Then copy-paste:
```python
from accounts.models import User

# Create admin
User.objects.create_user(username='admin', email='admin@test.com', password='admin123', role='ADMIN')
print("✅ Admin: admin/admin123")

# Create customer
User.objects.create_user(username='customer1', email='c1@test.com', password='cust123', role='CUSTOMER')
print("✅ Customer: customer1/cust123")

# Exit
exit()
```

## Login URLs

- **Home**: http://localhost:8000
- **Admin**: http://localhost:8000/admin/
- **Customer Dashboard**: http://localhost:8000/core/customer/dashboard/
- **Technician Dashboard**: http://localhost:8000/core/technician/dashboard/

## Stop Server
Press `Ctrl+C` or run:
```bash
lsof -ti:8000 | xargs kill -9
```

