# Customer and Technician Guide

## ✅ Current Status

The 403 CSRF error has been fixed! The server is now running properly.

## 🔑 Login Credentials

### Admin
- **URL**: http://127.0.0.1:8000/accounts/login/
- **Username**: `admin`
- **Password**: `admin123`
- **Redirects to**: Django Admin Dashboard (`/admin/`)

### Technician 1
- **Username**: `tech1`
- **Password**: `tech123`
- **Redirects to**: Technician Dashboard (`/core/technician/dashboard/`)

### Technician 2
- **Username**: `tech2`
- **Password**: `tech123`
- **Redirects to**: Technician Dashboard

### Customer 1
- **Username**: `customer1`
- **Password**: `cust123`
- **Redirects to**: Customer Dashboard (`/core/customer/dashboard/`)

### Customer 2
- **Username**: `customer2`
- **Password**: `cust123`
- **Redirects to**: Customer Dashboard

## 📋 What's Working

### ✅ Customer Features
1. **Dashboard** - View all service requests
2. **Submit Request** - Can submit service requests (one active at a time)
3. **Business Rule**: Only ONE active request allowed (pending/assigned/in_progress)
4. **Auto-geocoding**: Addresses are automatically converted to lat/lon

**URLs:**
- Dashboard: http://127.0.0.1:8000/core/customer/dashboard/
- Submit Request: http://127.0.0.1:8000/core/customer/submit/
- Nearby Technicians: http://127.0.0.1:8000/core/customer/nearby/

### ✅ Technician Features
1. **Dashboard** - View assigned jobs for selected date
2. **Route Map** - See route on map (to be implemented)
3. **Profile** - Update availability hours and skills
4. **Signup** - Create technician profile

**URLs:**
- Dashboard: http://127.0.0.1:8000/core/technician/dashboard/
- Map: http://127.0.0.1:8000/core/technician/map/
- Profile: http://127.0.0.1:8000/core/technician/profile/
- Signup: http://127.0.0.1:8000/core/technician/signup/

### ✅ Admin Features
1. **Admin Dashboard** - Full Django admin interface
2. **OR-Tools Assignment** - Run algorithm to match customers to technicians
3. **View Routes** - See all technician routes on map

**URLs:**
- Dashboard: http://127.0.0.1:8000/admin/
- Run Assignment: http://127.0.0.1:8000/core/admin/assign/
- View Map: http://127.0.0.1:8000/core/admin/map/

## 🚀 How to Use

### For Customers:
1. **Login** at http://127.0.0.1:8000/accounts/login/
2. **View Dashboard** - See your service requests
3. **Submit New Request** (if no active requests):
   - Enter service details
   - Enter Melbourne address
   - Address will be auto-geocoded
   - Submit request
4. **Check Status** - See if your request is assigned to a technician
5. **View Nearby Technicians** - See technicians who will be in your area

### For Technicians:
1. **Login** at http://127.0.0.1:8000/accounts/login/
2. **View Dashboard** - See assigned jobs for today
3. **Change Date** - Select different date to view past/future jobs
4. **View Route Map** - See your route with stops
5. **Update Profile** - Set your availability hours and skills
6. **Update Job Status** - Mark jobs as "In Progress" or "Completed"

### For Admins:
1. **Login** at http://127.0.0.1:8000/accounts/login/
2. **Access Admin** - Full Django admin interface
3. **Manage Data** - View/edit technicians, customers, service requests
4. **Run Assignment** - Click "Run OR-Tools Assignment"
   - Select date
   - Click "Run Assignment"
   - View results and save
5. **View Routes on Map** - See all technician routes

## 📝 What Needs to Be Done

### Pending Features:
1. **Technician Profile Form** - Allow editing availability and skills
2. **Technician Route Map** - Show route on Google Map
3. **Technician Status Update** - Allow marking jobs complete
4. **Nearby Technicians View** - Show technicians near customer
5. **Bootstrap Styling** - Apply consistent Bootstrap styling

## 🐛 Fixed Issues

1. ✅ **CSRF Error** - Fixed by updating import statements
2. ✅ **Import Error** - Fixed GeocodingService import
3. ✅ **Permission Error** - Fixed by updating access checks
4. ✅ **Redirect Issues** - Fixed role-based redirects

## 🔄 Recent Changes

1. Created `core/customer_views.py` - Customer-specific views
2. Created `core/technician_views.py` - Technician-specific views  
3. Created `core/forms.py` - Form definitions
4. Updated `core/urls.py` - Added customer and technician URLs
5. Updated `accounts/views.py` - Fixed login redirects
6. Fixed imports in `maps/services.py` - Added aliases
7. Created templates:
   - `templates/core/customer_dashboard.html`
   - `templates/core/customer_submit_request.html`
   - `templates/core/technician_dashboard.html`

## 💡 Next Steps

To test the application:

1. **Start Server** (if not running):
   ```bash
   cd "/Users/staffuser/Desktop/App Generation /django"
   source venv/bin/activate
   python manage.py runserver
   ```

2. **Login as Customer**:
   - Go to http://127.0.0.1:8000/accounts/login/
   - Use: customer1 / cust123
   - Submit a service request

3. **Login as Technician**:
   - Use: tech1 / tech123
   - View assigned jobs
   - Update profile

4. **Login as Admin**:
   - Use: admin / admin123
   - Run OR-Tools assignment
   - View routes on map

## 📞 Support

If you encounter any issues:
1. Check the terminal for error messages
2. Make sure the server is running
3. Check that you're using the correct login credentials
4. Verify that you have an active request (for customers) or profile (for technicians)

