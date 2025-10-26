# Local Testing Checklist

## ✅ Server is Running

Your Django app should be accessible at:
- **Home**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

## Test Accounts

Use these accounts to test different roles:

### Admin
- **URL**: http://127.0.0.1:8000/admin/
- **Username**: admin
- **Password**: admin123

### Customers
- **Customer 1**:
  - URL: http://127.0.0.1:8000/core/customer/dashboard/
  - Username: customer1
  - Password: cust123

- **Customer 2**:
  - Username: customer2
  - Password: cust123

### Technicians
- **Technician 1**:
  - URL: http://127.0.0.1:8000/core/technician/dashboard/
  - Username: tech1
  - Password: tech123

- **Technician 2**:
  - Username: tech2
  - Password: tech123

## Testing Checklist

### 1. ✅ Admin Dashboard
- [ ] Login as admin
- [ ] View all service requests
- [ ] View all technicians
- [ ] Access assignment tool at: http://127.0.0.1:8000/core/admin/assign/
- [ ] Run OR-Tools assignment
- [ ] View routes on map at: http://127.0.0.1:8000/core/admin/map/

### 2. ✅ Customer Features
- [ ] Register as new customer: http://127.0.0.1:8000/accounts/register/
- [ ] Login as customer1
- [ ] View dashboard with service requests
- [ ] Submit new service request: http://127.0.0.1:8000/core/customer/submit/
  - Test Google Places Autocomplete (type "Collins St")
  - Select service type
  - Choose time window
  - Select required skills
  - Submit
- [ ] View nearby technicians: http://127.0.0.1:8000/core/customer/nearby/

### 3. ✅ Technician Features
- [ ] Register as technician: http://127.0.0.1:8000/accounts/technician-signup/
  - Enter depot address (use Melbourne address)
  - Set shift times
  - Select skills
  - Test Google Places Autocomplete for depot
- [ ] Login as tech1
- [ ] View assigned jobs on dashboard
- [ ] View route on map: http://127.0.0.1:8000/core/technician/map/
- [ ] Update job status (Start Job → Complete Job)
- [ ] Update profile: http://127.0.0.1:8000/core/technician/profile/

### 4. ✅ OR-Tools Assignment
- [ ] Login as admin
- [ ] Go to: http://127.0.0.1:8000/core/admin/assign/
- [ ] Select date
- [ ] Click "Run Assignment" button
- [ ] Verify assignments are created
- [ ] View assignments in admin panel

### 5. ✅ Map Features
- [ ] Customer submits request with Melbourne address
- [ ] Address is geocoded automatically
- [ ] Admin assigns jobs
- [ ] View routes on admin map
- [ ] View technician's route on their map
- [ ] Verify polylines are drawn correctly
- [ ] Verify markers show depot and stops

### 6. ✅ Data Verification
- [ ] Check database has test data
- [ ] Verify ServiceRequests have lat/lon
- [ ] Verify Technicians have depot lat/lon
- [ ] Verify Assignments have sequence_order
- [ ] Verify route polylines are stored

## Common URLs

- **Home**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/
- **Customer**: /core/customer/dashboard/
- **Customer Submit**: /core/customer/submit/
- **Customer Nearby**: /core/customer/nearby/
- **Technician Dashboard**: /core/technician/dashboard/
- **Technician Map**: /core/technician/map/
- **Technician Profile**: /core/technician/profile/
- **Technician Signup**: /accounts/technician-signup/
- **Admin Assignment**: /core/admin/assign/
- **Admin Map**: /core/admin/map/

## Troubleshooting

### If Port Already in Use

```bash
# Find what's using port 8000
lsof -ti:8000

# Kill it
kill -9 $(lsof -ti:8000)

# Or use different port
python manage.py runserver 8001
```

### If Database is Empty

```bash
python manage.py populate_test_data
```

### If Migrations are Needed

```bash
python manage.py migrate
```

### If Superuser Doesn't Exist

```bash
python manage.py createsuperuser
```

## Expected Functionality

### Working Features:
✅ User authentication (login/logout/register)
✅ Role-based dashboards
✅ Customer service request submission
✅ Technician profile creation and updates
✅ Admin assignment interface
✅ OR-Tools solver
✅ Google Maps integration
✅ Timeline/schedule view
✅ Google Places Autocomplete

### Testing Prior to Deployment:
- [ ] All features work locally
- [ ] No console errors
- [ ] No database errors
- [ ] Maps load correctly
- [ ] OR-Tools assignments work
- [ ] All forms submit successfully

## Next Steps After Local Testing

Once everything works locally:
1. Push code to GitHub
2. Deploy to Koyeb/DigitalOcean
3. Configure production environment
4. Test on live URL

## Server Commands

**Stop Server:**
- Press Ctrl+C in terminal
- Or run: `kill $(lsof -ti:8000)`

**Restart Server:**
```bash
cd "/Users/staffuser/Desktop/App Generation /django"
source venv/bin/activate
python manage.py runserver
```

**View Logs:**
- Server output shows in terminal
- Check for any errors or warnings

**Access URLs:**
- http://127.0.0.1:8000/ - Home page
- http://127.0.0.1:8000/admin/ - Django admin

Your server should now be running! 🚀

