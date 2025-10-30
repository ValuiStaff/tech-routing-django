# Deploy to Koyeb and Create Admin User

## Quick Deployment Steps

### 1. Prepare and Push to GitHub

```bash
# Make sure you're in the project directory
cd "/Users/staffuser/Desktop/App Generation /django"

# Stage all changes
git add -A

# Commit
git commit -m "Ready for Koyeb deployment"

# Push to GitHub
git push origin main
```

### 2. Deploy on Koyeb

1. **Go to [Koyeb Dashboard](https://app.koyeb.com/)**
2. **Click "Create App"**
3. **Connect GitHub**:
   - Select "GitHub" as source
   - Authorize Koyeb to access your GitHub
   - Select your repository (e.g., `yourusername/tech-routing-django`)
4. **Build Settings**:
   - **Buildpack/Dockerfile**: Select "Dockerfile"
   - **Dockerfile path**: `Dockerfile` (should auto-detect)
5. **Click "Deploy"**

### 3. Add PostgreSQL Database

After the app starts deploying:

1. Go to **"Data"** tab in your Koyeb app
2. Click **"Create Database"**
3. Select **"PostgreSQL"**
4. Wait for database to provision (1-2 minutes)
5. Copy the **DATABASE_URL** (you'll need this)

### 4. Configure Environment Variables

In your app's **"Settings"** → **"Environment Variables"**, add:

```bash
# Required Settings
DEBUG=False
SECRET_KEY=<generate-random-key-see-below>
DJANGO_SETTINGS_MODULE=tech_routing.production_settings

# Database (from PostgreSQL service above)
DATABASE_URL=<paste-database-url-from-step-3>

# Google Maps API
GOOGLE_MAPS_API_KEY=<your-google-maps-api-key>

# Optional: Server settings
GUNICORN_WORKERS=3
GUNICORN_THREADS=2
GUNICORN_TIMEOUT=120
PORT=8000
```

**Generate SECRET_KEY** (run locally):
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as `SECRET_KEY` in environment variables.

### 5. Create Admin User on Koyeb

Once your app is deployed and running:

#### Method 1: Using Koyeb Web Console (Easiest)

1. Go to your app in Koyeb dashboard
2. Click **"Console"** tab
3. Click **"Open Console"**
4. Run the Django management command:
   ```bash
   python manage.py createsuperuser
   ```
5. Follow the prompts:
   - Username: (enter your admin username)
   - Email: (enter your email)
   - Password: (enter a secure password)
   - Password confirmation: (re-enter password)

#### Method 2: Using Django Shell

1. In Koyeb Console, run:
   ```python
   python manage.py shell
   ```
2. Then run:
   ```python
   from accounts.models import User
   user = User.objects.create_superuser(
       username='admin',
       email='admin@example.com',
       password='YourSecurePassword123!',
       role='ADMIN'
   )
   user.save()
   print("Admin user created successfully!")
   exit()
   ```

#### Method 3: One-Line Command (Alternative)

In Koyeb Console:
```bash
python manage.py shell -c "from accounts.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'YourSecurePassword123!', role='ADMIN')"
```

**Replace:**
- `admin` with your desired username
- `admin@example.com` with your email
- `YourSecurePassword123!` with a secure password

### 6. Access Admin Panel

1. Your app URL will be: `https://your-app-name.koyeb.app`
2. Go to: `https://your-app-name.koyeb.app/admin/`
3. Login with the credentials you created

### 7. Initial Setup on Koyeb

After logging in as admin:

1. **Configure Google Maps**:
   - Go to: `/admin/core/googlemapsconfig/`
   - Add your Google Maps API key
   - Set average speed (default: 40 km/h)

2. **Create Skills** (if needed):
   - Go to: `/admin/core/skill/`
   - Add skills like: Plumbing, Electric, HVAC, etc.

3. **Import Sample Data** (optional):
   - Use Bulk Upload feature at `/admin/bulk-upload/`
   - Upload the `sample_data_50_people.xlsx` file

## Quick Checklist

- [ ] Code pushed to GitHub
- [ ] Koyeb app created and connected to GitHub
- [ ] PostgreSQL database created
- [ ] Environment variables configured
- [ ] App deployed successfully
- [ ] Admin user created
- [ ] Can login to `/admin/`
- [ ] Google Maps API key configured
- [ ] Initial data loaded (optional)

## Troubleshooting

### Can't create superuser
- Make sure migrations ran: `python manage.py migrate`
- Check database connection is working

### Admin login fails
- Verify admin user was created: Check in Django shell
- Reset password if needed:
  ```python
  from accounts.models import User
  u = User.objects.get(username='admin')
  u.set_password('NewPassword123!')
  u.save()
  ```

### Database errors
- Verify DATABASE_URL is correct
- Check database service is running in Koyeb
- Wait a few minutes after creating database

### App not starting
- Check logs in Koyeb dashboard
- Verify all environment variables are set
- Ensure SECRET_KEY is not a placeholder

## View Logs

To see what's happening:
1. Go to your app in Koyeb
2. Click **"Logs"** tab
3. View real-time application logs

## Next Steps After Deployment

1. Set up custom domain (optional)
2. Configure email settings (for password resets)
3. Set up backups for PostgreSQL database
4. Monitor app performance in Koyeb dashboard

---

**Your app will be live at:** `https://your-app-name.koyeb.app`

**Admin panel:** `https://your-app-name.koyeb.app/admin/`

