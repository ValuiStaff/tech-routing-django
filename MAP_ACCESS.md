# How to View Routes on Map

## Access the Map

After running the assignment and creating assignments:

### Option 1: From Assignments List
1. Go to: http://127.0.0.1:8000/admin/core/assignment/
2. Click the **green "View Routes on Map" button**
3. You'll see all technician routes on an interactive Google Map

### Option 2: Direct URL
Go to: **http://127.0.0.1:8000/core/admin/map/**

### Option 3: With Date Filter
Go to: **http://127.0.0.1:8000/core/admin/map/?date=2025-10-26**

## What You'll See

- **Depot markers** (arrow shape) - starting point for each technician
- **Numbered stop markers** (circles) - customer locations in sequence
- **Colored polylines** - route path for each technician
- **Legend** - shows technician names and number of stops

## Map Features

- Each technician has a different color route
- Routes connect depot → stop 1 → stop 2 → ... → depot
- Interactive map you can zoom and pan
- Legend showing all active routes

## Requirements

- You need a valid Google Maps API key configured
- At least one assignment must exist for the selected date
- Both technicians and customers need valid lat/lon coordinates

## Current Status

✅ Map view created  
✅ Route visualization with polylines  
✅ Legend with technician colors  
✅ Depot and stop markers  

To test:
1. Run assignment first at: http://127.0.0.1:8000/admin/core/assignment/assign/
2. Then view map at: http://127.0.0.1:8000/core/admin/map/

