# Quick Deploy to Koyeb - Step by Step

## ⚡ Quick Steps (5 minutes)

### 1. Push to GitHub
```bash
git add -A
git commit -m "Ready for Koyeb deployment"
git push origin main
```

### 2. Create Koyeb App
1. Go to https://app.koyeb.com/
2. Click **"Create App"**
3. Connect **GitHub** → Select your repo
4. Build: **Dockerfile** (auto-detects)
5. Click **"Deploy"**

### 3. Add Database
1. In your app → **"Data"** tab
2. Click **"Create Database"** → **PostgreSQL**
3. Copy the **DATABASE_URL**

### 4. Add Environment Variables
In app **"Settings"** → **"Environment Variables"**:

**Generate SECRET_KEY** (run locally):
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Add these variables:
```
DEBUG=False
SECRET_KEY=<paste-generated-key>
DJANGO_SETTINGS_MODULE=tech_routing.production_settings
DATABASE_URL=<paste-database-url>
GOOGLE_MAPS_API_KEY=<your-maps-api-key>
```

### 5. Create Admin User

Once deployed, go to app → **"Console"** tab → Run:

**Option 1: Custom Command (Easiest)**
```bash
python manage.py create_admin --username admin --email your@email.com --password YourPassword123!
```

**Option 2: Django createsuperuser**
```bash
python manage.py createsuperuser
```

**Option 3: Django Shell**
```python
python manage.py shell
```
Then:
```python
from accounts.models import User
User.objects.create_superuser('admin', 'admin@example.com', 'YourPassword123!', role='ADMIN')
exit()
```

### 6. Access Your App
- **App URL**: `https://your-app-name.koyeb.app`
- **Admin Panel**: `https://your-app-name.koyeb.app/admin/`

---

## ✅ After Login

1. **Configure Google Maps**
   - Go to: `/admin/core/googlemapsconfig/`
   - Add API key

2. **Add Skills** (optional)
   - Go to: `/admin/core/skill/`
   - Add: Plumbing, Electric, HVAC, etc.

3. **Upload Sample Data** (optional)
   - Go to: `/admin/bulk-upload/`
   - Upload: `sample_data_50_people.xlsx`

---

**That's it! Your app is live! 🚀**
