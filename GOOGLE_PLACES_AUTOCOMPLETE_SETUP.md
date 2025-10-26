# Google Places Autocomplete Setup

## ✅ What's Implemented

The customer service request form now has **Google Places Autocomplete** for address input with suggestions as you type!

### Features:
1. **Service Type Dropdown** - Predefined service types (Gas Leak, Electrical, Plumbing, etc.)
2. **Address Autocomplete** - Google Maps-style suggestions for Melbourne addresses
3. **Skills Dropdown** - Multi-select dropdown of required skills
4. **Auto-geocoding** - Addresses automatically get lat/lon when submitted

## 🧪 Test the Autocomplete

### Option 1: Test Page
Visit: http://127.0.0.1:8000/core/test/autocomplete/
- Simple test page to verify Google Places is working
- Type a Melbourne address to see suggestions

### Option 2: Customer Form
1. **Login as customer**: customer1 / cust123
2. Go to: http://127.0.0.1:8000/core/customer/submit/
3. **Start typing** in the address field - you'll see Google Maps suggestions!

## 📝 How It Works

1. **Type in address field** → Google Places API suggests addresses
2. **Select a suggestion** → Full address is filled in automatically
3. **Submit form** → Address is geocoded to get lat/lon
4. **Auto-save coordinates** → Location is saved to database

## 🔧 Technical Details

### Files Modified:
- `core/forms.py` - Added service_type dropdown, updated widgets
- `core/customer_views.py` - Added API key to context
- `templates/core/customer_submit_request.html` - Added Google Places script
- `core/urls.py` - Added test route

### Google Places Configuration:
- **API Key**: Loaded from `GoogleMapsConfig` in database
- **Country Restriction**: Australia (`au`) only
- **Types**: Addresses only (not establishments)
- **Fields**: Formatted address + geometry (for geocoding)

## 🐛 Troubleshooting

If autocomplete doesn't appear:

1. **Check API Key**: Visit Django admin → Core → Google Maps Configs
2. **Verify Places API**: Make sure Google Places API is enabled in Google Cloud Console
3. **Check Browser Console**: Open Developer Tools (F12) to see any errors
4. **Test Page**: Visit http://127.0.0.1:8000/core/test/autocomplete/

## ✅ Current Status

✅ Service type dropdown - Working
✅ Address autocomplete - Implemented
✅ Skills dropdown - Working
✅ Auto-geocoding - Working

Server is running and ready for testing!

