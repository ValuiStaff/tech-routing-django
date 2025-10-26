# Install Defang CLI

## Manual Installation

Since automated installation had issues, here's the manual approach:

### Option 1: Download from GitHub (Recommended)

1. **Visit**: https://github.com/DefangLabs/defang/releases
2. **Download** the latest release for macOS (darwin-arm64 or darwin-amd64)
3. **Extract** the tar.gz file
4. **Move** the `defang` binary to your PATH:
```bash
sudo mv defang /usr/local/bin/
chmod +x /usr/local/bin/defang
```

### Option 2: Use Docker

If Defang CLI installation is problematic, you can run it via Docker:

```bash
# Create an alias for easy use
alias defang='docker run --rm -it -v $(pwd):/work defangio/defang'

# Or use directly
docker run --rm -it -v $(pwd):/work defangio/defang compose up
```

### Option 3: Build from Source

```bash
git clone https://github.com/DefangLabs/defang.git
cd defang
go build -o defang
sudo mv defang /usr/local/bin/
```

## Verify Installation

```bash
defang --version
```

## After Installation

Once Defang CLI is installed, you can deploy with:

```bash
# Deploy to Playground (free, no cloud account needed)
defang compose up --playground

# Or run the deployment script
./deploy_defang.sh
```

## Alternative: Use Pre-built Docker Image

If CLI installation continues to fail, I can help you deploy using Docker directly without the Defang CLI.

**Would you like me to:**
1. Create a pure Docker deployment approach?
2. Help with manual Defang CLI installation?
3. Switch to PythonAnywhere instead?

