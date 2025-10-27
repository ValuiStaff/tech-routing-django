# How to Add PostgreSQL to Koyeb

## Option 1: Add After Deployment (Recommended)

### Step 1: Go to Your App Dashboard
1. Visit https://app.koyeb.com/
2. Click on your deployed app

### Step 2: Add PostgreSQL Service
1. In your app, look for **"Add Service"** or **"Create Resource"** button
2. Click on it
3. Select **"Database"** or **"PostgreSQL"**
4. Configure:
   - **Name**: e.g., `tech-routing-db`
   - **Region**: Choose closest to you
   - **Version**: PostgreSQL 15 or 16
   - **Plan**: Free tier or starter ($5/month)
5. Click **"Create"**

### Step 3: Koyeb Auto-Connects
- Koyeb automatically adds `DATABASE_URL` environment variable
- Your app will automatically redeploy
- No manual configuration needed!

## Option 2: Add Before Deployment

### When Creating App:
1. Create App → Deploy from GitHub
2. Before deployment, look for **"Add Database"** option
3. Select PostgreSQL
4. Create and deploy together

## Add via Datastores (Centralized Management)

### Step 1: Create Datastore
1. Go to https://app.koyeb.com/datastores
2. Click **"Create Datastore"**
3. Select **"PostgreSQL"**
4. Configure and create

### Step 2: Link to Your App
1. Go to your app dashboard
2. Go to **Settings** → **Environment Variables**
3. Add variable:
   - **Name**: `DATABASE_URL`
   - **Value**: Copy from your datastore connection string
4. Save

## After Adding PostgreSQL

Your app will automatically:
- ✅ Connect to database
- ✅ Run migrations
- ✅ Create tables
- ✅ Ready to use!

## Import Your Data

Once PostgreSQL is connected:

1. Open your app shell (click "Exec" in Koyeb app dashboard)
2. Run:
   ```bash
   cd /app
   python manage.py loaddata production_data.json
   ```

## Verify It's Working

1. Check your app logs
2. Should see:
   ```
   Operations to perform:
     Apply all migrations...
   Running migrations...
     Applying account.0001_initial... OK
   ```

## Troubleshooting

### If DATABASE_URL not auto-added:
1. Go to Datastore
2. Copy connection string
3. Add to app environment variables

### If connection fails:
1. Check PostgreSQL is running
2. Verify `DATABASE_URL` format
3. Wait for app to redeploy

## Quick Steps Summary

1. ✅ Deploy app first (without DB)
2. ✅ Add PostgreSQL service
3. ✅ Koyeb auto-connects it
4. ✅ Import your data
5. ✅ Done!

## Need Help?

- Check Koyeb logs in app dashboard
- Verify environment variables
- Ensure PostgreSQL is running

