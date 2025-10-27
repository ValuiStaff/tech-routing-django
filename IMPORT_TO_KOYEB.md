# Import Local Data to Koyeb - Complete Instructions

## ✅ Your Data is Ready!

You have `production_data.json` file that contains all your local database data:
- ✅ 9 users (admin, technicians, customers)
- ✅ All technicians with skills
- ✅ All service requests
- ✅ All assignments
- ✅ Google Maps configuration

## Step-by-Step: Import to Koyeb

### Step 1: Deploy Your App to Koyeb
(Follow `COMPLETE_KOYEB_SETUP.md` if not already deployed)

### Step 2: Add PostgreSQL Database
1. Go to your Koyeb app dashboard
2. Click **"Add Service"** or **"Datastores"**
3. Create **PostgreSQL** database
4. Koyeb auto-adds `DATABASE_URL` to your app

### Step 3: Wait for App to Deploy
- App will automatically redeploy with database
- Should show successful build
- App URL: `https://your-app-name.koyeb.app`

### Step 4: Access Koyeb Shell

**Option A: From App Dashboard**
1. Go to your app in Koyeb
2. Click **"Exec"** button (opens terminal)

**Option B: Via Browser**
1. Terminal window should open in your browser
2. You'll see: `root@...:/app#`

### Step 5: Import Your Data

In the Koyeb shell, run these commands:

```bash
# Navigate to app directory (you should already be there)
cd /app

# Verify the data file exists (it's in your GitHub repo)
ls -lh production_data.json

# Run migrations first (creates database tables)
python manage.py migrate --noinput

# Import your local data
python manage.py loaddata production_data.json
```

**Expected Output:**
```
Operations to perform:
  Apply all migrations...
Running migrations...
  Applying accounts.0001_initial... OK
  Applying core.0001_initial... OK
  ...
Installed 9 object(s) from 1 fixture(s)
```

This means your data is imported!

### Step 6: Verify Import

Check that users were imported:

```bash
python manage.py shell
```

Then in Python:
```python
from accounts.models import User
print(f"Total users: {User.objects.count()}")
for user in User.objects.all():
    print(f"- {user.username} ({user.email}) - Role: {user.role}")
exit()
```

You should see all 9 users!

### Step 7: Create Superuser (If Needed)

If you want to create a NEW admin user:

```bash
python manage.py createsuperuser
```

Enter:
- Username: (e.g., `newadmin`)
- Email: (e.g., `admin@example.com`)
- Password: (create strong password)

### Step 8: Login to Your App

Now you can login with your local credentials:

#### Admin Login:
- **URL**: `https://your-app-name.koyeb.app/admin`
- **Username**: `admin`
- **Password**: *(same as your local admin password)*

#### Customer Login:
- **URL**: `https://your-app-name.koyeb.app/accounts/login/`
- **Username**: `customer1`, `customer2`, `georgie`, `julie`, or `nirjhara`
- **Password**: *(same as your local customer password)*

#### Technician Login:
- **URL**: `https://your-app-name.koyeb.app/accounts/login/`
- **Username**: `tech1`, `tech2`, or `nav`
- **Password**: *(same as your local technician password)*

## Your Imported Data

### Users (9 total):
1. **admin** - Admin user (admin@test.com)
2. **tech1** - Technician (tech1@test.com)
3. **tech2** - Technician (tech2@test.com)
4. **nav** - Technician (nav@email.com)
5. **customer1** - Customer (customer1@test.com)
6. **customer2** - Customer (customer2@test.com)
7. **georgie** - Customer (cust100@gmail.com)
8. **julie** - Customer (julie@email.com)
9. **nirjhara** - Customer (nirjhara@email.com)

### Also Imported:
- ✅ All Technicians with their skills
- ✅ All Service Requests
- ✅ All Assignments
- ✅ All Skills
- ✅ Google Maps Configuration

## Troubleshooting

### "No such file or directory" Error?

The `production_data.json` file is in your GitHub repo. If it's not showing:

```bash
# List files in app directory
ls -la

# If file not there, it might be in a different location
find . -name "production_data.json"

# If still not found, download from GitHub
curl -o production_data.json https://raw.githubusercontent.com/ValuiStaff/tech-routing-django/main/production_data.json
```

### "FixtureNotFound" Error?

Make sure file name is correct:
```bash
# Check file exists
ls production_data.json

# If different name, use correct name
python manage.py loaddata your_file_name.json
```

### "Duplicate Key" or "Integrity Error"?

Data might already be imported. Try:
```bash
# Clear database first
python manage.py flush --noinput

# Then import
python manage.py migrate --noinput
python manage.py loaddata production_data.json
```

### Password Not Working?

If you can't remember passwords:
1. Create new superuser: `python manage.py createsuperuser`
2. Login as new admin
3. Go to Admin → Users
4. Reset passwords for other users

## Quick Commands Reference

```bash
# Access Koyeb shell
# (Click "Exec" in app dashboard)

# Basic commands
cd /app
ls -la

# Check database connection
python manage.py dbshell

# Run migrations
python manage.py migrate

# Import data
python manage.py loaddata production_data.json

# Create superuser
python manage.py createsuperuser

# Django shell
python manage.py shell
```

## Success Checklist

- [ ] App deployed on Koyeb
- [ ] PostgreSQL database added
- [ ] Accessed Koyeb shell
- [ ] Ran migrations successfully
- [ ] Imported production_data.json
- [ ] Verified users exist
- [ ] Can login with local credentials
- [ ] Can access admin panel
- [ ] Can login as customer
- [ ] Can login as technician

## You're Done! 🎉

After importing the data, your Koyeb app now has:
- ✅ All your local users
- ✅ All technicians with skills
- ✅ All service requests
- ✅ All assignments
- ✅ Google Maps config

**You can now login to your deployed app using the same credentials as your local app!**

Visit: `https://your-app-name.koyeb.app`

