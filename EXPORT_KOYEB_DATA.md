# Export Data from Koyeb PostgreSQL Database

## Methods to Export Data from Koyeb

### Method 1: Using Koyeb Shell (Recommended)

#### Step 1: Access Your App Shell
1. Go to https://app.koyeb.com/
2. Click on your app
3. Click **"Exec"** or **"Shell"** button
4. Terminal will open

#### Step 2: Export Data to JSON
Run this command in the Koyeb shell:

```bash
cd /app
python manage.py dumpdata --indent 2 > exported_data.json
```

This creates `exported_data.json` in your app directory.

#### Step 3: Download the File

**Option A: If file is visible in Koyeb UI**
- Look for file manager or download button
- Download the file

**Option B: Using curl or wget**
```bash
# Get the file via URL (if Koyeb exposes it)
curl https://your-app.koyeb.app/exported_data.json -o exported_data.json
```

**Option C: Using scp or sftp** (if available)
- Use the connection info from Koyeb
- Connect via SFTP
- Download the file

---

### Method 2: Using Django Management Command

#### Step 1: Access Shell
Same as Method 1, Step 1

#### Step 2: Export Specific Models
```bash
cd /app

# Export all data
python manage.py dumpdata --indent 2 > all_data.json

# Export only Users
python manage.py dumpdata accounts.User --indent 2 > users.json

# Export only Technicians
python manage.py dumpdata core.Technician --indent 2 > technicians.json

# Export only Service Requests
python manage.py dumpdata core.ServiceRequest --indent 2 > service_requests.json

# Export multiple models
python manage.py dumpdata accounts.User core.Technician core.ServiceRequest --indent 2 > important_data.json
```

#### Step 3: Download via Koyeb CLI (if installed)

If you have Koyeb CLI installed:

```bash
# Download file from app
koyeb app exec your-app-name
cd /app
python manage.py dumpdata --indent 2 > exported_data.json
exit

# Copy file to local machine
koyeb app exec your-app-name -- cat /app/exported_data.json > exported_data.json
```

---

### Method 3: Direct PostgreSQL Export (pg_dump)

#### Step 1: Get PostgreSQL Connection Info

1. Go to Koyeb dashboard
2. Go to your **Datastores** section
3. Click on your PostgreSQL database
4. Copy the connection string:
   - Looks like: `postgres://user:password@host:port/dbname`

#### Step 2: Export using pg_dump

**Option A: Using psql in Koyeb Shell**

```bash
# In Koyeb app shell
cd /app

# Connect to database and export
pg_dump "postgres://user:password@host:port/dbname" > backup.sql

# Or export as JSON (if installed)
pg_dump -Fc "postgres://user:password@host:port/dbname" > backup.dump
```

**Option B: From Local Machine**

If you have `pg_dump` installed locally:

```bash
# Export entire database
pg_dump "postgres://user:password@host:port/dbname" > koyeb_backup.sql

# Export specific tables
pg_dump "postgres://user:password@host:port/dbname" -t accounts_user -t core_technician > tables_backup.sql

# Export as custom format
pg_dump "postgres://user:password@host:port/dbname" -Fc > backup.dump
```

---

### Method 4: Export Specific Data (Python Script)

Create a management command or run Python script in Koyeb shell:

#### Step 1: Access Shell
Go to your app → Exec → Open terminal

#### Step 2: Create Python Script

```bash
cd /app
python manage.py shell
```

Then run:

```python
import json
from accounts.models import User
from core.models import Technician, ServiceRequest, Assignment

# Export all users
users = User.objects.all()
users_data = []
for user in users:
    users_data.append({
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'first_name': user.first_name,
        'last_name': user.last_name,
    })

with open('users_export.json', 'w') as f:
    json.dump(users_data, f, indent=2)

print("Users exported to users_export.json")

# Export technicians
technicians = Technician.objects.all()
techs_data = []
for tech in technicians:
    techs_data.append({
        'username': tech.user.username,
        'depot_address': tech.depot_address,
        'depot_lat': float(tech.depot_lat),
        'depot_lon': float(tech.depot_lon),
        'capacity_minutes': tech.capacity_minutes,
        'shift_start': str(tech.shift_start),
        'shift_end': str(tech.shift_end),
    })

with open('technicians_export.json', 'w') as f:
    json.dump(techs_data, f, indent=2)

print("Technicians exported to technicians_export.json")

# Similar for other models...

exit()
```

---

### Method 5: Using Koyeb Dashboard (If Available)

Some Koyeb interfaces have a **"Backup"** or **"Export"** feature:

1. Go to your datastore
2. Click **"Backup"** or **"Export"**
3. Choose format: SQL, JSON, CSV
4. Download file

---

## Most Practical Method

### Using Django dumpdata (Easiest):

#### In Koyeb Shell:

```bash
# Export everything
cd /app
python manage.py dumpdata --indent 2 > complete_backup.json

# View the file
cat complete_backup.json

# Copy output and save locally
# OR download via Koyeb UI if available
```

### Downloading from Koyeb:

**Option 1: If you can access files directly**
1. Go to app dashboard
2. Find **"Files"** or **"Storage"** section
3. Download the JSON file

**Option 2: Output to logs**
```bash
cd /app
python manage.py dumpdata --indent 2 | tee exported_data.json
# Copy from terminal output
```

**Option 3: Email yourself**
```bash
cd /app
python manage.py dumpdata --indent 2 > exported_data.json

# If sendmail is available
mail -s "Database Export" your-email@example.com < exported_data.json
```

---

## Backup Strategy

### Daily/Weekly Backups:

Create a management command that exports and stores backups:

```python
# core/management/commands/backup_data.py
from django.core.management.base import BaseCommand
import subprocess
from datetime import datetime

class Command(BaseCommand):
    help = 'Export database to JSON backup'

    def handle(self, *args, **options):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backup_{timestamp}.json'
        
        subprocess.run([
            'python', 'manage.py', 'dumpdata',
            '--indent', '2',
            '--output', filename
        ])
        
        self.stdout.write(f'Backup created: {filename}')
```

**Run daily:**
```bash
# In Koyeb shell or as cron job
python manage.py backup_data
```

---

## Verify Your Export

After exporting:

```bash
# Check file exists
ls -lh exported_data.json

# Check file size
wc -l exported_data.json

# View first few lines
head -20 exported_data.json

# Count objects
python -c "import json; data = json.load(open('exported_data.json')); print(f'Total objects: {len(data)}')"
```

---

## What's Included in Export

When you run `dumpdata`, it exports:
- ✅ All User accounts
- ✅ All Technicians
- ✅ All Service Requests
- ✅ All Assignments
- ✅ All Skills
- ✅ Google Maps Config
- ✅ Admin log entries
- ✅ Permissions
- ✅ All app data

---

## Import to New Database

If you need to import the exported data:

```bash
cd /app
python manage.py loaddata exported_data.json
```

---

## Quick Reference

### Export Commands:

```bash
# Complete database export
python manage.py dumpdata --indent 2 > backup.json

# Specific apps only
python manage.py dumpdata accounts core --indent 2 > backup.json

# Specific models only
python manage.py dumpdata accounts.User core.ServiceRequest --indent 2 > backup.json

# Exclude some apps (e.g., sessions)
python manage.py dumpdata --exclude sessions --indent 2 > backup.json
```

### Import Commands:

```bash
# Import complete backup
python manage.py loaddata backup.json

# Import and override
python manage.py loaddata --verbosity 2 backup.json
```

---

## Your Exported Data File

Your app already has `production_data.json` exported from local database:
- File: `production_data.json`
- Size: ~23KB
- Contains: All your local data

After deploying to Koyeb and importing this file, you can export fresh data from Koyeb at any time using the methods above!

