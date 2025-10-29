#!/bin/bash

# Upload data to Koyeb
# This script shows the steps to upload data_for_koyeb.json to Koyeb

echo "=========================================="
echo "Data Export Ready for Koyeb"
echo "=========================================="
echo ""
echo "File: data_for_koyeb.json (20KB)"
echo "Records: Users, Skills, Technicians, Service Requests"
echo ""
echo "Next steps:"
echo "------------------------------------------"
echo "1. Go to Koyeb Dashboard: https://app.koyeb.com/"
echo "2. Select your app: tech-routing-django"
echo "3. Click 'Console' tab (left sidebar)"
echo "4. Click 'Open Console'"
echo ""
echo "Then in the console, choose one of:"
echo ""
echo "Option A: Direct upload via console"
echo "  cat > data_for_koyeb.json << 'ENDOFFILE'"
echo "  (then paste the file content)"
echo "  ENDOFFILE"
echo "  python manage.py loaddata data_for_koyeb.json"
echo ""
echo "Option B: Use nano editor"
echo "  nano data_for_koyeb.json"
echo "  (paste content, Ctrl+X, Y, Enter)"
echo "  python manage.py loaddata data_for_koyeb.json"
echo ""
echo "Option C: Use vi editor"
echo "  vi data_for_koyeb.json"
echo "  (press i to insert, paste content)"
echo "  (press Esc, then :wq to save)"
echo "  python manage.py loaddata data_for_koyeb.json"
echo ""
echo "=========================================="
echo ""
echo "Would you like to see the file content? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    less data_for_koyeb.json
fi

