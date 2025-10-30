#!/bin/bash
# Export data for Koyeb deployment
# This script exports all necessary data from local database

echo "📦 Exporting data for Koyeb..."

# Export all essential data
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

echo "✅ Export complete: koyeb_export.json"
echo ""
echo "📊 File size:"
ls -lh koyeb_export.json
echo ""
echo "📝 Next steps:"
echo "1. Upload koyeb_export.json to Koyeb"
echo "2. Use Koyeb Console: python manage.py loaddata koyeb_export.json"
echo ""
echo "⚠️  Note: If you want to create a new admin user on Koyeb,"
echo "   you may want to exclude User data or manually edit the file."

