# How to Load Data on Koyeb (Without CLI)

## Method 1: Using Koyeb Web Console

### Step 1: Export data locally
On your local machine:
```bash
cd /Users/staffuser/Desktop/App\ Generation\ /django
source venv/bin/activate
python manage.py dumpdata > data.json
```

### Step 2: Access Koyeb Console
1. Go to https://app.koyeb.com/
2. Select your app: **tech-routing-django**
3. Click **Console** tab (left sidebar)
4. Click **Open Console** button

### Step 3: Create data.json in Koyeb Console
In the console, you have a few options:

**Option A: Using echo command (for small files)**
```bash
# Open a text editor in your local machine
cat data.json

# Copy the entire output
# In Koyeb console, type:
cat > data.json << 'EOF'
# Paste the JSON content here
EOF
```

**Option B: Using vi editor (for large files)**
```bash
# In Koyeb console
vi data.json
# Press 'i' to enter insert mode
# Paste your JSON content
# Press Esc
# Type :wq to save and exit
```

**Option C: Using nano (easier for beginners)**
```bash
nano data.json
# Paste your JSON content
# Press Ctrl+X
# Press Y to confirm
# Press Enter to save
```

### Step 4: Load data
```bash
python manage.py loaddata data.json
```

## Method 2: Direct Django Shell (Recommended for small data)

If you need to create sample data instead of importing:

### Step 1: Open Django shell in Koyeb Console
```bash
python manage.py shell
```

### Step 2: Run these commands in Python shell
```python
from accounts.models import User
from core.models import Skill, Technician, ServiceRequest

# Create admin user (if not exists)
admin, created = User.objects.get_or_create(username='admin', defaults={
    'email': 'admin@example.com',
    'is_staff': True,
    'is_superuser': True
})
if created:
    admin.set_password('admin123')
    admin.save()
    print("Admin user created!")
else:
    print("Admin user already exists")

# Create skills
skills_data = ['Plumbing', 'Electric', 'HVAC', 'IT', 'Roofing', 'Gas', 'Solar']
for skill_name in skills_data:
    skill, created = Skill.objects.get_or_create(name=skill_name)
    print(f"Skill: {skill_name} - {'created' if created else 'exists'}")

print("\nNext, use the admin panel to create technicians and service requests")
exit()
```

### Step 3: Create technician via admin
1. Go to your Koyeb app URL
2. Login as admin
3. Go to admin panel
4. Create users and technicians

## Method 3: Using Bulk Upload Feature

The easiest way is to use the bulk upload feature in the admin panel:

1. Login to admin panel on your deployed app
2. Go to **Bulk Upload Users** (from admin index)
3. Use **Manual Entry** to create users and service requests
4. All data will be created immediately

## Troubleshooting

**Problem: Cannot paste in console**
- Make sure you're in insert mode (press 'i' in vi, or use Ctrl+V)

**Problem: File too large**
- Try Method 2 or 3 instead
- Or split data.json into smaller files

**Problem: Permission denied**
- Make sure you're in /app directory
- Files created in console are temporary, consider using database instead

## Quick Commands Cheat Sheet

```bash
# Check current directory
pwd

# List files
ls -la

# Create file with content
cat > myfile.json << 'EOF'
{"content": "here"}
EOF

# View file
cat myfile.json

# Edit file
vi myfile.json
# or
nano myfile.json

# Run Django management command
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata data.json

# Exit console
exit
```

