# 📦 Nimbus Installation Guide

Complete guide for installing Nimbus backup solution on various platforms.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Installation](#quick-installation)
- [Manual Installation](#manual-installation)
- [Platform-Specific Instructions](#platform-specific-instructions)
- [Optional Features](#optional-features)
- [Development Installation](#development-installation)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

---

## Prerequisites

### Required

- **Python 3.8 or higher**
- **pip** (Python package manager)
- **Git** (for cloning repository)

### Optional

- **virtualenv** or **venv** (recommended)
- **Docker** (for containerized deployment - coming soon)

---

## Quick Installation

The fastest way to get Nimbus up and running:

```bash
# Clone the repository
git clone https://github.com/ysntns/nimbus.git
cd nimbus

# Run automatic installer
chmod +x scripts/install.sh
./scripts/install.sh

# Activate virtual environment
source venv/bin/activate

# Verify installation
nimbus --version
```

That's it! You're ready to use Nimbus.

---

## Manual Installation

If you prefer to install manually:

### Step 1: Clone Repository

```bash
git clone https://github.com/ysntns/nimbus.git
cd nimbus
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Step 4: Install Nimbus

```bash
# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Step 5: Verify Installation

```bash
# Check version
nimbus --version

# Show help
nimbus --help

# Test backup command
nimbus backup --help
```

---

## Platform-Specific Instructions

### Linux

#### Ubuntu/Debian

```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# Install Nimbus
git clone https://github.com/ysntns/nimbus.git
cd nimbus
./scripts/install.sh
```

#### Fedora/RHEL/CentOS

```bash
# Install Python and pip
sudo dnf install python3 python3-pip git

# Install Nimbus
git clone https://github.com/ysntns/nimbus.git
cd nimbus
./scripts/install.sh
```

#### Arch Linux

```bash
# Install Python and pip
sudo pacman -S python python-pip git

# Install Nimbus
git clone https://github.com/ysntns/nimbus.git
cd nimbus
./scripts/install.sh
```

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python3 git

# Install Nimbus
git clone https://github.com/ysntns/nimbus.git
cd nimbus
./scripts/install.sh
```

### Windows

1. Install Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. Install Git from [git-scm.com](https://git-scm.com/download/win)
3. Open PowerShell or Command Prompt:

```powershell
# Clone repository
git clone https://github.com/ysntns/nimbus.git
cd nimbus

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Nimbus
pip install -e .
```

---

## Optional Features

Install additional features based on your needs:

### GUI Support (Coming Soon)

```bash
pip install nimbus-backup[gui]
```

This installs:
- PyQt6
- PyQt6-WebEngine

### Cloud Providers Support (Coming Soon)

```bash
pip install nimbus-backup[cloud]
```

This installs:
- google-api-python-client (Google Drive)
- dropbox (Dropbox)
- boto3 (AWS S3)

### Encryption Support (Coming Soon)

```bash
pip install nimbus-backup[crypto]
```

This installs:
- cryptography

### Scheduling Support (Coming Soon)

```bash
pip install nimbus-backup[scheduler]
```

This installs:
- apscheduler

### All Features

```bash
pip install nimbus-backup[all]
```

---

## Development Installation

For contributing to Nimbus:

### Step 1: Fork and Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/nimbus.git
cd nimbus
```

### Step 2: Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Step 3: Install Development Tools

```bash
# Install development tools
pip install black isort flake8 mypy pytest pytest-cov
```

### Step 4: Verify Development Setup

```bash
# Run tests
pytest

# Check formatting
black --check app/ tests/

# Check imports
isort --check-only app/ tests/

# Lint code
flake8 app/ tests/

# Type check
mypy app/
```

---

## Configuration

### Default Configuration

Nimbus creates configuration files in:
- Linux/macOS: `~/.config/nimbus/`
- Windows: `%APPDATA%\nimbus\`

Default configuration includes:
- `config.yaml` - Main configuration
- `providers.yaml` - Cloud provider settings
- `logs/` - Log files directory
- `keys/` - Encryption keys directory
- `backups/` - Local backup metadata

### Customizing Configuration

Edit `~/.config/nimbus/config.yaml`:

```yaml
backup:
  compression: true
  encryption: false
  incremental: true
  verify_backup: true

performance:
  threads: 4
  chunk_size: 10MB

logging:
  level: INFO
  file: ~/.config/nimbus/logs/nimbus.log
```

---

## Troubleshooting

### Python Version Issues

```bash
# Check Python version
python3 --version

# Should be 3.8 or higher
# If not, install newer Python version
```

### Permission Errors

```bash
# Linux/macOS: Use --user flag
pip install --user -e .

# Or fix permissions
sudo chown -R $USER:$USER ~/.local/
```

### Import Errors

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Command Not Found

```bash
# Check if nimbus is in PATH
which nimbus

# If not, use full path or reinstall
pip install -e . --force-reinstall
```

### Dependencies Conflict

```bash
# Create fresh virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

---

## Uninstallation

### Complete Removal

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv/

# Uninstall package
pip uninstall nimbus-backup

# Remove configuration (optional)
rm -rf ~/.config/nimbus/

# Remove cloned repository
cd ..
rm -rf nimbus/
```

### Keep Configuration

```bash
# Only remove package and venv
deactivate
rm -rf venv/
pip uninstall nimbus-backup

# Configuration remains in ~/.config/nimbus/
```

---

## Verification

After installation, verify everything works:

```bash
# Check version
nimbus --version

# Show help
nimbus --help

# Test configuration
nimbus config show

# Perform test backup
mkdir -p /tmp/test_source /tmp/test_backup
echo "test file" > /tmp/test_source/test.txt
nimbus backup /tmp/test_source -d /tmp/test_backup

# Verify backup
ls -la /tmp/test_backup/

# Cleanup
rm -rf /tmp/test_source /tmp/test_backup
```

---

## Next Steps

After successful installation:

1. **Read the documentation**: `cat README.md`
2. **Configure Nimbus**: `nimbus config show`
3. **Perform first backup**: `nimbus backup --help`
4. **Set up schedules**: `nimbus schedule add` (coming soon)
5. **Explore features**: `nimbus --help`

---

## Support

If you encounter issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Search [existing issues](https://github.com/ysntns/nimbus/issues)
3. Create a [new issue](https://github.com/ysntns/nimbus/issues/new)
4. Join [Discussions](https://github.com/ysntns/nimbus/discussions)

---

## Links

- [Main Documentation](../README.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Changelog](../CHANGELOG.md)
- [GitHub Repository](https://github.com/ysntns/nimbus)

---

Made with ❤️ by Yasin TANIŞ
