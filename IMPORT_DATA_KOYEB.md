# Import Local Data to Koyeb

## Quick Steps

### 1. Export Data Locally

Run the export script:
```bash
chmod +x export_data.sh
./export_data.sh
```

Or manually:
```bash
python manage.py dumpdata \
    accounts.User \
    core.Skill \
    core.Technician \
    core.ServiceRequest \
    core.GoogleMapsConfig \
    --indent 2 \
    --natural-foreign \
    --natural-primary \
    -o koyeb_export.json
```

This creates `koyeb_export.json` with all your local data.

### 2. Upload to Koyeb

You have several options:

#### Option A: Upload via Koyeb Console (Recommended)

1. **Go to your Koyeb app dashboard**
2. **Click "Console" tab**
3. **Click "Upload File"** button
4. **Select `koyeb_export.json`**
5. **Wait for upload to complete**

#### Option B: Using Koyeb CLI

```bash
# Install Koyeb CLI if needed
brew install koyeb/tap/koyeb  # macOS
# or
curl -fsSL https://koyeb.com/install.sh | bash  # Linux

# Upload and import
koyeb files upload <your-app-name> koyeb_export.json
```

#### Option C: Copy-paste via Console

1. Open `koyeb_export.json` locally
2. Copy all content
3. In Koyeb Console, run:
   ```bash
   cat > koyeb_export.json << 'EOF'
   [paste your JSON content here]
   EOF
   ```

### 3. Import Data on Koyeb

In Koyeb Console, run:

```bash
python manage.py loaddata koyeb_export.json
```

### 4. Verify Import

Check if data was imported:
```bash
python manage.py shell
```

Then:
```python
from accounts.models import User
from core.models import Skill, Technician, ServiceRequest

print(f"Users: {User.objects.count()}")
print(f"Skills: {Skill.objects.count()}")
print(f"Technicians: {Technician.objects.count()}")
print(f"Service Requests: {ServiceRequest.objects.count()}")
exit()
```

## Important Notes

### Admin User

- If `koyeb_export.json` includes an admin user, you can:
  - **Option 1**: Import it and use those credentials
  - **Option 2**: Skip importing users, create new admin:
    ```bash
    python manage.py dumpdata \
        core.Skill \
        core.Technician \
        core.ServiceRequest \
        core.GoogleMapsConfig \
        --indent 2 -o koyeb_export_no_users.json
    
    # Then import without users
    python manage.py loaddata koyeb_export_no_users.json
    python manage.py create_admin --username admin --email admin@example.com --password YourPassword123!
    ```

### Google Maps API Key

After importing, you may need to update the Google Maps API key:
```python
python manage.py shell
```
```python
from core.models import GoogleMapsConfig
config = GoogleMapsConfig.load()
config.api_key = 'YOUR_KOYEB_GOOGLE_MAPS_API_KEY'
config.save()
exit()
```

Or via admin panel:
- Go to: `/admin/core/googlemapsconfig/1/change/`
- Update API key
- Save

### Excluding Sensitive Data

If you want to exclude users (to create fresh admin):
```bash
python manage.py dumpdata \
    core.Skill \
    core.Technician \
    core.ServiceRequest \
    core.GoogleMapsConfig \
    --indent 2 \
    --natural-foreign \
    --natural-primary \
    -o koyeb_export_no_users.json
```

## Troubleshooting

### Import fails with duplicate entries
- Clear existing data first (if testing):
  ```bash
  python manage.py shell
  ```
  ```python
  from core.models import *
  ServiceRequest.objects.all().delete()
  Technician.objects.all().delete()
  Skill.objects.all().delete()
  exit()
  ```

### Large file upload issues
- Use Koyeb CLI for large files
- Or split the JSON into smaller chunks
- Or use the Bulk Upload feature in admin panel instead

### Password hashes not working
- The exported password hashes should work
- If not, reset passwords via Django shell:
  ```python
  from accounts.models import User
  user = User.objects.get(username='admin')
  user.set_password('NewPassword123!')
  user.save()
  ```

## Alternative: Use Bulk Upload

Instead of importing JSON, you can use the bulk upload feature:

1. Go to: `/admin/bulk-upload/`
2. Upload `sample_data_50_people.xlsx`
3. All users, technicians, and service requests will be created

This is easier if you just want to import sample data!

