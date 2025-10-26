# Setup Instructions

## Quick Start with Virtual Environment

### 1. Create Virtual Environment

```bash
cd "/Users/staffuser/Desktop/App Generation /django"
python3 -m venv venv
```

### 2. Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create Test Data

```bash
python manage.py populate_test_data
```

### 6. Configure Google Maps API Key

1. Go to: http://127.0.0.1:8000/admin/core/googlemapsconfig/1/change/
2. Or use Django shell:
```bash
python manage.py shell
```
```python
from core.models import GoogleMapsConfig
config = GoogleMapsConfig.load()
config.api_key = 'YOUR_GOOGLE_MAPS_API_KEY_HERE'
config.save()
exit()
```

### 7. Run Server

```bash
python manage.py runserver
```

Server will start at: http://127.0.0.1:8000/

## Test Credentials

- **Admin**: admin / admin123
- **Technician 1**: tech1 / tech123
- **Technician 2**: tech2 / tech123
- **Customer 1**: customer1 / cust123
- **Customer 2**: customer2 / cust123

## Assign Jobs

Visit: http://127.0.0.1:8000/core/admin/assign/

## Deactivate Virtual Environment

When you're done working:
```bash
deactivate
```

## Troubleshooting

If you get "command not found" errors:
- Make sure virtual environment is activated
- Check that you're in the project directory
- Try: `which python` (should point to venv/python)

