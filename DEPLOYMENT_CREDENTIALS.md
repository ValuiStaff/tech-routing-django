# Deployment Credentials - Your Koyeb App Login Info

## 📋 Your Users (from Local Database)

After you import `production_data.json` into your Koyeb PostgreSQL database, these are your login credentials:

### Admin Users:
- **Username**: `admin`
- **Email**: admin@test.com
- **Password**: *(same as your local admin password)*
- **Role**: ADMIN (Superuser)

### Technician Users:
- **Username**: `tech1`
- **Email**: tech1@test.com
- **Password**: *(same as your local tech1 password)*
- **Role**: TECHNICIAN

- **Username**: `tech2`
- **Email**: tech2@test.com
- **Password**: *(same as your local tech2 password)*
- **Role**: TECHNICIAN

- **Username**: `nav`
- **Email**: nav@email.com
- **Password**: *(same as your local nav password)*
- **Role**: TECHNICIAN

### Customer Users:
- **Username**: `customer1`
- **Email**: customer1@test.com
- **Password**: *(same as your local customer1 password)*
- **Role**: CUSTOMER

- **Username**: `customer2`
- **Email**: customer2@test.com
- **Password**: *(same as your local customer2 password)*
- **Role**: CUSTOMER

- **Username**: `georgie`
- **Email**: cust100@gmail.com
- **Password**: *(same as your local georgie password)*
- **Role**: CUSTOMER

- **Username**: `julie`
- **Email**: julie@email.com
- **Password**: *(same as your local julie password)*
- **Role**: CUSTOMER

- **Username**: `nirjhara`
- **Email**: nirjhara@email.com
- **Password**: *(same as your local nirjhara password)*
- **Role**: CUSTOMER

## 🚨 If You Don't Remember Passwords

### Option 1: Use Django Admin to Reset

After deployment:

1. Go to: `https://your-app-name.koyeb.app/admin`
2. Login with admin account (if you remember that password)
3. Go to: **Accounts** → **Users**
4. Click on any user
5. Scroll to **"Change Password"** section
6. Set new password
7. Save

### Option 2: Create New Users

Access Koyeb shell and run:

```bash
# Create new admin
python manage.py createsuperuser

# Or create users via Django shell
python manage.py shell
```

Then in the shell:
```python
from accounts.models import User

# Create new admin
User.objects.create_user(
    username='newadmin',
    email='newadmin@example.com',
    password='newpass123',
    role='ADMIN',
    is_superuser=True,
    is_staff=True
)

# Create new technician
User.objects.create_user(
    username='newtech',
    email='newtech@example.com',
    password='newpass123',
    role='TECHNICIAN'
)

# Create new customer
User.objects.create_user(
    username='newcustomer',
    email='newcustomer@example.com',
    password='newpass123',
    role='CUSTOMER'
)
```

### Option 3: Check Local Passwords

Check your local database for what the passwords were:

```bash
cd "/Users/staffuser/Desktop/App Generation /django"
source venv/bin/activate
python manage.py shell
```

Then:
```python
from accounts.models import User
users = User.objects.all()
for user in users:
    print(f"Username: {user.username}, Email: {user.email}")
```

## 📝 How to Import Data After Deployment

1. **Go to Koyeb App Dashboard**
2. **Click "Exec"** or **"Shell"** button
3. Run these commands:

```bash
cd /app
python manage.py loaddata production_data.json
```

This will import all your users with their existing passwords.

## ✅ Quick Reference

### Admin Login:
- **URL**: `https://your-app-name.koyeb.app/admin`
- **Username**: `admin`
- **Password**: *(Your local admin password)*

### Customer Login:
- **URL**: `https://your-app-name.koyeb.app/accounts/login/`
- **Username**: `customer1` or `customer2` or any customer username
- **Password**: *(Your local customer password)*

### Technician Login:
- **URL**: `https://your-app-name.koyeb.app/accounts/login/`
- **Username**: `tech1` or `tech2` or `nav`
- **Password**: *(Your local technician password)*

## 🔑 Important Notes

1. **Passwords are preserved**: When you import `production_data.json`, user passwords are imported as-is
2. **Hashed passwords**: Passwords are stored as Django hashes, so they're the same as your local database
3. **If you don't remember**: Use Option 1 or 2 above to create new users or reset passwords

## 🎯 Next Steps

1. Deploy your app to Koyeb
2. Add PostgreSQL database
3. Import `production_data.json`
4. Login with any of the usernames above
5. Use the same password you had locally

## Need Help?

If you can't remember any passwords:
1. Create a new superuser: `python manage.py createsuperuser` in Koyeb shell
2. Then reset other user passwords from Django admin

