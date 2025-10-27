# Complete Koyeb Setup - App + Database + Data Import

## Step-by-Step Guide: Deploy App with All Your Data

### Step 1: Generate SECRET_KEY

Open your terminal and run:

```bash
cd "/Users/staffuser/Desktop/App Generation /django"
source venv/bin/activate
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Copy this SECRET_KEY** - you'll need it later!

Example output:
```
django-insecure-7n2@&#n-x3s7-51jfp0%hz+-&o6aca0$pmd=hnc&(%3^8j3ev5
```

---

### Step 2: Create App on Koyeb

1. **Go to**: https://app.koyeb.com/
2. **Sign up** or **Log in** (if you haven't already)
3. **Click "Create App"** (top right button)
4. **Select "Deploy from GitHub"**
5. **Authorize Koyeb** to access your GitHub (if asked)
6. **Select repository**: `ValuiStaff/tech-routing-django`
7. **Select branch**: `main`
8. **Click "Next"**

---

### Step 3: Configure Build Settings

On the build configuration page:

- **Build Command**: Leave **EMPTY** (Dockerfile handles this)
- **Run Command**: Leave **EMPTY** (Dockerfile CMD handles this)
- **Click "Next"** or **"Continue"**

---

### Step 4: Add PostgreSQL Database Service

#### Method 1: Add Service During Deployment

1. You'll see **"Services"** or **"Add Service"** section
2. **Click "Add Service"** button
3. Select **"Database"** or **"PostgreSQL"**
4. Fill in:
   - **Name**: `tech-routing-db` (or any name)
   - **Region**: Choose closest (e.g., `us-east`)
   - **Plan**: `Starter` ($5/month) or Free tier
5. **Click "Create"** or **"Add"**

#### Method 2: Add Database After Deployment

If you've already deployed without database:

1. Go to your **app dashboard**
2. Look for **"Add Service"** or **"Datastores"**
3. Click **"Create Datastore"**
4. Select **PostgreSQL**
5. Configure same as above
6. Koyeb will auto-add `DATABASE_URL` environment variable

---

### Step 5: Set Environment Variables

Now set up your app configuration:

1. Click on **"Environment Variables"** or **"Variables"** tab
2. Click **"Add Variable"** for each variable below

**Add these variables:**

#### Variable 1:
- **Name**: `DJANGO_SETTINGS_MODULE`
- **Value**: `tech_routing.production_settings`

#### Variable 2:
- **Name**: `DEBUG`
- **Value**: `False`

#### Variable 3:
- **Name**: `SECRET_KEY`
- **Value**: `(paste your generated key from Step 1)`

#### Variable 4:
- **Name**: `GOOGLE_MAPS_API_KEY`
- **Value**: `(your Google Maps API key)`

#### Check:
- **DATABASE_URL** should be automatically added by Koyeb when you create PostgreSQL

**After adding all variables:**
- Click **"Save"** or **"Deploy"**

---

### Step 6: Deploy Your App

1. Click **"Deploy"** button
2. **Wait 5-10 minutes** for build
3. Watch the **logs** (they'll show progress)

**What you'll see:**
```
✅ Building Docker image
✅ Installing dependencies
✅ Collecting static files: 127 files copied
✅ Running migrations
✅ Starting server
✅ Deploy successful!
```

**When done:**
- Green checkmark appears
- Your app URL: `https://your-app-name.koyeb.app`

---

### Step 7: Verify Deployment

1. Visit: `https://your-app-name.koyeb.app`
2. Visit health check: `https://your-app-name.koyeb.app/health/`
3. Should return: `{"status": "ok", "service": "tech-routing"}`

---

### Step 8: Import Your Local Data

Now import all your local database data to Koyeb PostgreSQL:

#### Access Koyeb Shell:

1. Go to your **app dashboard** in Koyeb
2. Click **"Exec"** button (opens terminal)
3. Terminal will open

#### Import Data:

Run these commands in the terminal:

```bash
# Navigate to app directory
cd /app

# Run migrations (creates database tables)
python manage.py migrate --noinput

# Import your local data
python manage.py loaddata production_data.json
```

**You should see:**
```
Installed 9 object(s) from 1 fixture(s)
```

This means your data is imported!

---

### Step 9: Verify Your Data

#### Check Users:

Run in Koyeb shell:

```bash
python manage.py shell
```

Then:
```python
from accounts.models import User
users = User.objects.all()
for user in users:
    print(f"Username: {user.username}, Email: {user.email}, Role: {user.role}")
exit()
```

You should see all your users!

---

### Step 10: Login to Your App

#### Admin Login:
- **URL**: `https://your-app-name.koyeb.app/admin`
- **Username**: `admin`
- **Password**: (same as your local admin password)

#### Customer Login:
- **URL**: `https://your-app-name.koyeb.app/accounts/login/`
- **Username**: `customer1` or `customer2` or `georgie` or `julie` or `nirjhara`
- **Password**: (same as your local customer password)

#### Technician Login:
- **URL**: `https://your-app-name.koyeb.app/accounts/login/`
- **Username**: `tech1` or `tech2` or `nav`
- **Password**: (same as your local technician password)

---

### Step 11: Configure Google Maps

1. Login as admin: `https://your-app-name.koyeb.app/admin`
2. Navigate: **Core → Google Maps Configs**
3. Click on existing config
4. Enter your **Google Maps API key**
5. Set **Average Speed**: `50` km/h
6. Click **"Save"**

---

### ✅ Complete! Your App is Live with All Data!

## What You Have Now:

✅ App deployed on Koyeb  
✅ PostgreSQL database connected  
✅ All local data imported  
✅ All users available  
✅ Technicians with skills configured  
✅ Service requests imported  
✅ Google Maps configured  
✅ Ready to use!

## Quick Reference:

### Your App URLs:
- **App**: `https://your-app-name.koyeb.app`
- **Admin**: `https://your-app-name.koyeb.app/admin`
- **Health**: `https://your-app-name.koyeb.app/health/`

### All Your Users (9 total):

**Admins:**
- `admin` (admin@test.com)

**Technicians:**
- `tech1` (tech1@test.com)
- `tech2` (tech2@test.com)
- `nav` (nav@email.com)

**Customers:**
- `customer1` (customer1@test.com)
- `customer2` (customer2@test.com)
- `georgie` (cust100@gmail.com)
- `julie` (julie@email.com)
- `nirjhara` (nirjhara@email.com)

### Passwords:
All users keep their passwords from your local database. If you don't remember them, see "Can't Remember Password?" section below.

---

## Troubleshooting

### Can't Remember Passwords?

**Create New Superuser:**
```bash
# In Koyeb shell
cd /app
python manage.py createsuperuser
```

**Reset User Password in Admin:**
1. Login as admin
2. Go to: **Accounts → Users**
3. Click on any user
4. Scroll to **"Change Password"**
5. Set new password

### Database Not Connected?

**Check environment variables:**
1. Go to app → **Settings** → **Environment Variables**
2. Verify `DATABASE_URL` exists
3. Should be: `postgres://user:pass@host:port/dbname`

### Import Failed?

**Check data file exists:**
```bash
ls -lh /app/production_data.json
```

**Try import again:**
```bash
cd /app
python manage.py loaddata production_data.json
```

### App Crashes?

**Check logs:**
1. Go to app dashboard
2. Click **"Logs"** tab
3. Read error messages
4. Common issues:
   - Missing `GOOGLE_MAPS_API_KEY`
   - Invalid `SECRET_KEY`
   - Database connection failed

---

## Summary Checklist:

- [ ] Generated SECRET_KEY
- [ ] Created Koyeb account
- [ ] Deployed app from GitHub
- [ ] Added PostgreSQL database
- [ ] Set all environment variables
- [ ] App deployed successfully
- [ ] Accessed Koyeb shell
- [ ] Imported production_data.json
- [ ] Verified users exist
- [ ] Can login as admin
- [ ] Configured Google Maps
- [ ] App fully functional

---

## You're Done! 🎉

Your Django Tech Routing app is now:
- ✅ Live on Koyeb
- ✅ Connected to PostgreSQL
- ✅ Has all your local data
- ✅ Ready to use!

Visit: `https://your-app-name.koyeb.app`

