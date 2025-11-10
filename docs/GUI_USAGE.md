# Nimbus GUI Usage Guide

## Overview

Nimbus offers two GUI interfaces:
1. **CustomTkinter GUI** (Recommended) - Modern, beautiful interface
2. **PyQt6 GUI** - Traditional, feature-complete interface

## CustomTkinter GUI (v3.0)

### Installation

```bash
# Install GUI dependencies
pip install customtkinter pillow darkdetect

# Or install all optional dependencies
pip install -r requirements-optional.txt
```

### Launching

```bash
# Method 1: Use the launcher script
./nimbus-gui

# Method 2: Python module
python -m app.gui.main_window_ctk
```

### Features

#### 1. Backup Tab
Create and manage backups with these options:
- **Source**: Select directory to backup
- **Destination**: Select backup location
- **Incremental Backup**: Only backup changed files
- **Encryption**: AES-256-GCM encryption
- **Compression**: Reduce storage space
- **Verification**: SHA256 integrity checking
- **Real-time Progress**: Live progress bar and log

#### 2. Cloud Sync Tab
Upload backups to cloud storage:
- **Supported Providers**:
  - Google Drive (Active)
  - Dropbox (Coming Soon)
  - OneDrive (Coming Soon)
  - AWS S3 (Coming Soon)
  - Azure Blob (Coming Soon)

**Google Drive Setup**:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable Google Drive API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials.json
6. Save to `~/.nimbus/credentials.json`
7. Click "Connect to Google Drive" in the GUI
8. Follow browser authentication flow

#### 3. Restore Tab
Restore from previous backups:
- Browse available backups
- View backup details (date, type, files)
- Select restore destination
- Monitor restoration progress
- Automatic decryption if needed

#### 4. Schedule Tab
Automate backups with scheduling:
- **Frequency Options**:
  - Hourly
  - Daily
  - Weekly
  - Monthly
- **Time Selection**: Choose specific time
- **Day Selection**: For weekly backups
- **Options**: Set encryption, compression, etc.
- **Manage Schedules**: Pause or delete existing schedules

#### 5. History Tab
View all past backups:
- Chronological list view
- Backup details (name, date, type)
- File count
- Status indicators (encrypted, compressed, verified)
- Visual cards for easy browsing

#### 6. Settings Tab
Configure application preferences:
- **Theme**: Dark, Light, or System
- **Default Backup Location**: Set default path
- **Default Options**: Configure backup defaults
- **Notifications**: Enable/disable notifications
- **Advanced**: Max concurrent operations

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Browse source directory |
| Ctrl+S | Start backup |
| Ctrl+R | Refresh history |
| Ctrl+, | Open settings |
| F5 | Refresh current tab |

### Theme Support

The GUI supports three themes:
- **Dark**: Dark mode (default)
- **Light**: Light mode
- **System**: Follow system theme

Change theme in Settings tab.

### Troubleshooting

#### GUI doesn't launch
```bash
# Check dependencies
pip list | grep customtkinter

# Reinstall if needed
pip install --upgrade customtkinter pillow darkdetect
```

#### Authentication issues (Google Drive)
1. Check `~/.nimbus/credentials.json` exists
2. Delete `~/.nimbus/token.pickle` and re-authenticate
3. Ensure Google Drive API is enabled in Cloud Console

#### Progress bar not updating
- This is normal for very fast operations
- Check the log text area for detailed progress

## PyQt6 GUI (v2.1.0)

### Installation

```bash
pip install PyQt6
```

### Launching

```bash
python -m app.gui.main_window
```

## Comparison

| Feature | CustomTkinter GUI | PyQt6 GUI |
|---------|-------------------|-----------|
| Modern Look | ✅ | ❌ |
| Theme Support | ✅ Dark/Light/System | ❌ |
| Tab Interface | ✅ | ✅ |
| Restore Tab | ✅ | ❌ |
| Schedule Tab | ✅ | ✅ |
| Cloud Sync | ✅ | ✅ |
| Easy Installation | ✅ | ❌ (Large dep) |
| Cross-platform | ✅ | ✅ |

## Tips

1. **First Backup**: Always do a full backup first
2. **Incremental**: Use incremental for daily backups
3. **Encryption**: Enable for sensitive data
4. **Verification**: Enable for critical backups
5. **Cloud**: Test with small directory first
6. **Schedules**: Start with daily, adjust as needed

## Support

For issues or questions:
- GitHub Issues: https://github.com/ysntns/Nimbus/issues
- Email: ysn.tnss@gmail.com
- Documentation: https://github.com/ysntns/Nimbus/wiki
