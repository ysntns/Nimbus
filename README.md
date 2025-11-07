# 🌥️ Nimbus - Enterprise Backup & Cloud Sync Solution

<div align="center">

**Professional-grade backup and cloud synchronization solution for Linux systems**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Documentation](#documentation) • [Contributing](#contributing)

</div>

---

## 📋 Overview

**Nimbus** is an enterprise-grade backup solution designed for system administrators, developers, and power users who need reliable, automated, and secure backup capabilities. With support for multiple cloud providers, encryption, incremental backups, and real-time monitoring, Nimbus ensures your data is always protected.

## ✨ Features

### 🎯 Core Capabilities

- **📦 Full & Incremental Backups**: Smart backup engine that only copies changed files
- **☁️ Multi-Cloud Support**: Google Drive, Dropbox, OneDrive, AWS S3 (Coming soon)
- **🔐 AES-256 Encryption**: Military-grade encryption for sensitive data (Coming soon)
- **🔄 Automatic Scheduling**: Set it and forget it with APScheduler (Coming soon)
- **📊 Real-time Monitoring**: Track backup progress with beautiful CLI interface
- **🎨 Modern GUI**: PyQt6-based desktop application (Coming soon)
- **✅ Integrity Verification**: SHA-256 checksum validation for every file
- **⚡ Multi-threading**: Blazing fast backups with concurrent file processing
- **🔄 Resume Capability**: Continue interrupted backups seamlessly
- **📝 Detailed Logging**: Comprehensive logs with loguru
- **🎛️ Flexible Configuration**: YAML-based configuration system
- **🔔 Smart Notifications**: Email, Telegram, desktop notifications (Coming soon)

### 🛠️ Technical Features

- **Modern Python 3.8+**: Type hints, async support, modern syntax
- **Clean Architecture**: Modular, testable, maintainable codebase
- **Comprehensive Testing**: Unit and integration tests with pytest
- **CI/CD Pipeline**: Automated testing with GitHub Actions
- **Cross-platform**: Linux, macOS, Windows support
- **CLI & GUI**: Choose your preferred interface
- **Plugin System**: Extensible architecture for custom providers
- **Docker Support**: Containerized deployment (Coming soon)

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/ysntns/nimbus.git
cd nimbus

# Run automatic installer
./scripts/install.sh
```

### Manual Installation

```bash
# Clone repository
git clone https://github.com/ysntns/nimbus.git
cd nimbus

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Install from PyPI (Coming soon)

```bash
pip install nimbus-backup
```

### Install with Optional Features

```bash
# GUI support
pip install nimbus-backup[gui]

# Cloud providers support
pip install nimbus-backup[cloud]

# Encryption support
pip install nimbus-backup[crypto]

# Scheduling support
pip install nimbus-backup[scheduler]

# Install everything
pip install nimbus-backup[all]
```

---

## 💻 Usage

### CLI Interface

#### Basic Backup

```bash
# Full backup
nimbus backup /path/to/source --destination /path/to/backup

# Incremental backup (only changed files)
nimbus backup /path/to/source -d /path/to/backup --incremental

# With encryption
nimbus backup /path/to/source -d /path/to/backup --encrypt

# With compression
nimbus backup /path/to/source -d /path/to/backup --compress
```

#### Restore Backup

```bash
# Restore from backup
nimbus restore /path/to/backup /path/to/restore
```

#### Configuration Management

```bash
# Show current configuration
nimbus config show

# Set configuration value
nimbus config set backup.compression true
nimbus config set performance.threads 8

# Reset to defaults
nimbus config reset
```

#### Schedule Management (Coming soon)

```bash
# Add scheduled backup
nimbus schedule add \
  --source ~/Documents \
  --destination /backup/docs \
  --time "23:00" \
  --frequency daily

# List schedules
nimbus schedule list

# Remove schedule
nimbus schedule remove <schedule-id>
```

### Python API

```python
from pathlib import Path
from app.core.backup import BackupEngine, IncrementalBackup
from app.core.config import config

# Configure backup
source = Path('/path/to/source')
destination = Path('/path/to/backup')

# Full backup
engine = BackupEngine(source, destination)
stats = engine.backup()
print(f"Backed up {stats['backed_up_files']} files")

# Incremental backup
incremental = IncrementalBackup(source, destination)
stats = incremental.backup()
print(f"Backed up {stats['backed_up_files']} changed files")

# Restore
engine.restore(Path('/path/to/restore'))

# Custom configuration
config.set('performance.threads', 8)
config.set('backup.compression', True)
config.save()
```

### Progress Callbacks

```python
def progress_callback(data):
    print(f"Progress: {data['percentage']:.1f}%")
    print(f"Files: {data['backed_up_files']}/{data['total_files']}")
    print(f"Size: {data['transferred_size'] / (1024**3):.2f} GB")

engine = BackupEngine(source, destination)
engine.backup(progress_callback=progress_callback)
```

---

## 📁 Project Structure

```
nimbus/
├── app/                          # Main application package
│   ├── __init__.py               # Package metadata
│   ├── core/                     # Core backup engine
│   │   ├── backup.py             # Backup engine implementation
│   │   └── config.py             # Configuration manager
│   ├── cli/                      # Command-line interface
│   │   └── main.py               # CLI entry point
│   ├── gui/                      # GUI application (Coming soon)
│   ├── cloud/                    # Cloud provider integrations
│   ├── crypto/                   # Encryption modules
│   ├── scheduler/                # Task scheduling
│   └── utils/                    # Utility functions
├── config/                       # Configuration files
│   └── settings.yaml             # Default settings
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   └── integration/              # Integration tests
├── docs/                         # Documentation
│   ├── INSTALLATION.md           # Installation guide
│   └── api/                      # API documentation
├── scripts/                      # Utility scripts
│   ├── install.sh                # Installation script
│   └── deploy-github.sh          # Deployment script
├── resources/                    # Application resources
│   ├── icons/                    # Icons
│   └── themes/                   # GUI themes
├── .github/                      # GitHub configuration
│   ├── workflows/                # CI/CD pipelines
│   └── ISSUE_TEMPLATE/           # Issue templates
├── requirements.txt              # Dependencies
├── setup.py                      # Package setup
├── README.md                     # This file
├── LICENSE                       # MIT License
├── CONTRIBUTING.md               # Contribution guidelines
├── CHANGELOG.md                  # Version history
└── PROJECT_SUMMARY.md            # Project overview
```

---

## ⚙️ Configuration

Nimbus uses YAML configuration files stored in `~/.config/nimbus/`.

### Default Configuration

```yaml
backup:
  compression: true
  encryption: false
  incremental: true
  verify_backup: true
  exclude_patterns:
    - "*.tmp"
    - "__pycache__"
    - ".git"
    - "node_modules"

performance:
  threads: 4
  chunk_size: 10MB
  retry_attempts: 3
  timeout: 300

logging:
  level: INFO
  file: ~/.config/nimbus/logs/nimbus.log
  max_size: 100MB
  backup_count: 10

notifications:
  desktop: true
  email: false
  on_success: true
  on_failure: true
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_backup.py

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

---

## 📚 Documentation

- **[Installation Guide](docs/INSTALLATION.md)**: Detailed installation instructions
- **[Contributing Guide](CONTRIBUTING.md)**: How to contribute to Nimbus
- **[GitHub Deployment](GITHUB_DEPLOYMENT.md)**: Deploy to GitHub
- **[API Documentation](docs/api/)**: Complete API reference
- **[Changelog](CHANGELOG.md)**: Version history and changes

---

## 🗺️ Roadmap

### v2.0.0 (Current - Q1 2025)
- [x] Core backup engine
- [x] CLI interface
- [x] Incremental backup
- [x] Configuration system
- [x] Unit tests
- [x] Documentation

### v2.1.0 (Q2 2025)
- [ ] PyQt6 GUI application
- [ ] Cloud provider integrations (Google Drive, Dropbox)
- [ ] AES-256 encryption
- [ ] APScheduler integration
- [ ] Email notifications

### v2.2.0 (Q3 2025)
- [ ] AWS S3 support
- [ ] OneDrive integration
- [ ] Telegram notifications
- [ ] Web dashboard
- [ ] Docker support

### v3.0.0 (Q4 2025)
- [ ] Plugin system
- [ ] Multi-user support
- [ ] REST API
- [ ] Mobile app
- [ ] Enterprise features

---

## 🤝 Contributing

We welcome contributions from the community! Please read our [Contributing Guide](CONTRIBUTING.md) to get started.

### Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🧪 Write tests
- 💻 Submit pull requests

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/ysntns/nimbus.git
cd nimbus

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black app/ tests/
isort app/ tests/

# Lint code
flake8 app/ tests/
mypy app/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Yasin TANIŞ**

- 📧 Email: [ysn.tnss@gmail.com](mailto:ysn.tnss@gmail.com)
- 🐙 GitHub: [@ysntns](https://github.com/ysntns)
- 💼 LinkedIn: [ysntns](https://www.linkedin.com/in/ysntns)
- 🌐 Website: [cerebrai-vortx.com](https://cerebrai-vortx.com)
- 📍 Location: Şanlıurfa, Turkey

---

## 🙏 Acknowledgments

- **Click**: Beautiful command-line interfaces
- **Rich**: Rich text and beautiful formatting in the terminal
- **Loguru**: Simplified logging
- **PyYAML**: YAML parser and emitter
- **psutil**: Cross-platform process and system utilities

---

## 📊 Stats

![GitHub Stars](https://img.shields.io/github/stars/ysntns/nimbus?style=social)
![GitHub Forks](https://img.shields.io/github/forks/ysntns/nimbus?style=social)
![GitHub Issues](https://img.shields.io/github/issues/ysntns/nimbus)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/ysntns/nimbus)

---

## 🔗 Links

- [GitHub Repository](https://github.com/ysntns/nimbus)
- [Issue Tracker](https://github.com/ysntns/nimbus/issues)
- [Discussions](https://github.com/ysntns/nimbus/discussions)
- [Releases](https://github.com/ysntns/nimbus/releases)

---

<div align="center">

Made with ❤️ by Yasin TANIŞ

**If you find Nimbus useful, please consider giving it a ⭐️!**

</div>
