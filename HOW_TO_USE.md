# How to Use the Assignment Feature

## Access the Assign Button

After logging in as **admin**:

### Option 1: Direct URL
Go to: **http://127.0.0.1:8000/core/admin/assign/**

### Option 2: From Django Admin
1. Go to Django admin: http://127.0.0.1:8000/admin/
2. Navigate to **CORE** → **Service Requests** or **Assignments**
3. Look for pending requests
4. Access the assignment interface via the URL above

## Steps to Assign Jobs

1. **Login as Admin**
   - Username: `admin`
   - Password: `admin123`

2. **Go to Assignment Page**
   - Visit: http://127.0.0.1:8000/core/admin/assign/

3. **Select Date**
   - Choose the date you want to assign jobs for
   - Default is today's date

4. **Click "Run Assignment" Button**
   - The OR-Tools algorithm will:
     - Match customers to technicians based on skills
     - Respect time windows
     - Optimize travel time
     - Create assignments

5. **View Results**
   - You'll see success message with number of jobs assigned
   - Navigate to Django admin → CORE → Assignments
   - View the created assignments

6. **Check Assignments**
   - Go to: http://127.0.0.1:8000/admin/core/assignment/
   - You'll see all assignments with:
     - Technician name
     - Customer/Service request
     - Planned start/finish times
     - Sequence order

## Current Status

✅ Test data is populated:
- 2 Technicians (tech1, tech2)  
- 2 Customers (customer1, customer2)
- 2 Service requests (pending status)
- All addresses geocoded to Melbourne locations

⚠️ **Required before using assignment:**
- **Configure Google Maps API Key** in Django admin:
  1. Go to: http://127.0.0.1:8000/admin/core/googlemapsconfig/1/change/
  2. Enter your Google Maps API key
  3. Save

## Test the Assignment

Once API key is configured:

1. Login as admin
2. Go to: http://127.0.0.1:8000/core/admin/assign/
3. Click "Run Assignment"
4. Check results in Django admin assignments list

## What Happens When You Click "Assign"

1. Algorithm reads all pending service requests
2. Checks active technicians with valid depot coordinates
3. Matches based on:
   - Required skills (customer needs gas/plumbing/etc)
   - Time windows
   - Capacity (technician's daily capacity in minutes)
   - Travel time optimization
4. Creates Assignment records
5. Updates ServiceRequest status to "assigned"
6. Shows total travel time

## Map View (Coming Soon)

After assignments are created, you can view routes on map:
- URL: http://127.0.0.1:8000/core/admin/map/?date=2025-10-26

## Notes

- Only one active request per customer (business rule)
- All addresses must be in Melbourne
- Technicians need valid depot lat/lon coordinates
- API key required for geocoding

