# Paste Data Directly in Koyeb Console

## 🚀 Quick Method: Copy-Paste JSON Directly

### Step 1: Open the Export File Locally

```bash
# On your local machine
cat koyeb_export.json
```

Or just open `koyeb_export.json` in your text editor and select all content (Cmd+A / Ctrl+A), then copy it.

### Step 2: In Koyeb Console

1. **Go to your Koyeb app** → **"Console" tab** → **"Open Console"**

2. **Create the file and paste content:**
   ```bash
   cat > koyeb_export.json << 'EOF'
   ```
   
3. **Paste your entire JSON content here** (everything from `koyeb_export.json`)

4. **After pasting, on a new line, type:**
   ```
   EOF
   ```
   
5. **Press Enter**

6. **Import the data:**
   ```bash
   python manage.py loaddata koyeb_export.json
   ```

---

## 📋 Complete Example:

### In Koyeb Console, run:

```bash
cat > koyeb_export.json << 'EOF'
[
{
  "model": "accounts.user",
  "fields": {
    "password": "pbkdf2_sha256$...",
    ...
  }
},
...
]
EOF
```

**(Paste your entire JSON content where `...` is shown above)**

Then:
```bash
python manage.py loaddata koyeb_export.json
```

---

## 🎯 Alternative: Direct Python Import (Smaller Data)

If the file is too large, you can paste directly into Python shell:

### In Koyeb Console:

```bash
python manage.py shell
```

Then paste this code (replace `[...]` with your actual JSON content):

```python
import json
from django.core.management import call_command
from io import StringIO

# Paste your JSON content here
json_content = """[
{
  "model": "accounts.user",
  "fields": {
    ...
  }
}
]"""

# Save to file
with open('koyeb_export.json', 'w') as f:
    f.write(json_content)

# Load data
call_command('loaddata', 'koyeb_export.json')
exit()
```

---

## ✂️ Step-by-Step Visual Guide:

### Method 1: Using `cat` with heredoc (Recommended)

1. **In Koyeb Console**, type:
   ```bash
   cat > koyeb_export.json << 'EOF'
   ```

2. **Press Enter** (you'll see the cursor waiting)

3. **Paste your entire `koyeb_export.json` content**

4. **Press Enter** to go to new line

5. **Type `EOF`** on the new line

6. **Press Enter** (file is created)

7. **Run import:**
   ```bash
   python manage.py loaddata koyeb_export.json
   ```

### Method 2: Using `nano` editor (If console supports)

```bash
nano koyeb_export.json
```

- Paste content (right-click or Cmd+V / Ctrl+V)
- Press `Ctrl+X` to exit
- Press `Y` to save
- Press `Enter` to confirm

Then:
```bash
python manage.py loaddata koyeb_export.json
```

---

## 💡 Tips:

1. **Verify file was created:**
   ```bash
   ls -lh koyeb_export.json
   cat koyeb_export.json | head -20
   ```

2. **Check file size:**
   ```bash
   wc -l koyeb_export.json
   ```

3. **If paste fails**, try splitting into smaller chunks or use the **Bulk Upload** feature in admin panel instead.

---

## 🎬 Quick Copy Command (Local Machine)

To quickly copy the entire file content on macOS:
```bash
pbcopy < koyeb_export.json
```
Then just paste (Cmd+V) in Koyeb console after `cat > koyeb_export.json << 'EOF'`

---

**The easiest method is Method 1 using `cat > file << 'EOF'`!**

