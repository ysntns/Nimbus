# Nimbus Snap Package Installation

## Quick Install from Snap Store

Once published, install Nimbus with:

```bash
sudo snap install nimbus-backup
```

## Building Snap Locally

### Prerequisites

Install snapcraft:

```bash
sudo snap install snapcraft --classic
```

### Build Steps

1. Clone the repository:
```bash
git clone https://github.com/ysntns/Nimbus.git
cd Nimbus
```

2. Build the snap:
```bash
snapcraft
```

This will create `nimbus-backup_3.0_amd64.snap` (or `arm64` depending on your architecture).

3. Install locally:
```bash
sudo snap install nimbus-backup_3.0_*.snap --dangerous
```

The `--dangerous` flag is required for locally built snaps.

## Running Nimbus

### GUI Application

Launch from application menu or:
```bash
nimbus-backup.nimbus-gui
```

### Command Line

```bash
nimbus-backup
```

## Permissions

The snap requires the following permissions:
- `home` - Access to your home directory for backups
- `network` - Network access for cloud synchronization
- `removable-media` - Access to external drives (requires connection)

To allow access to removable media:
```bash
sudo snap connect nimbus-backup:removable-media
```

## Configuration

Configuration files are stored in:
```
$HOME/snap/nimbus-backup/current/.nimbus/
```

Google Drive credentials should be placed at:
```
$HOME/snap/nimbus-backup/current/.nimbus/credentials.json
```

## Publishing to Snap Store

### 1. Login to Snapcraft

```bash
snapcraft login
```

### 2. Register the snap name

```bash
snapcraft register nimbus-backup
```

### 3. Upload the snap

```bash
snapcraft upload nimbus-backup_3.0_*.snap --release=stable
```

### 4. Set up automatic builds (Optional)

Link your GitHub repository to Snapcraft for automatic builds on push:

1. Visit https://snapcraft.io/
2. Go to "My Snaps"
3. Click "Register a snap name"
4. Connect your GitHub repository
5. Enable automatic builds

## Snap Store Listing

### Required Information

- **Title**: Nimbus Backup
- **Summary**: Enterprise-grade backup and cloud synchronization solution
- **Description**: See snapcraft.yaml
- **License**: MIT
- **Website**: https://github.com/ysntns/Nimbus
- **Contact**: ysn.tnss@gmail.com
- **Categories**: Utilities, Productivity
- **Screenshots**: (Add GUI screenshots)
- **Icon**: snap/gui/nimbus-icon.png

### Update Icon

Replace `snap/gui/nimbus-icon.png` with your custom logo (256x256 PNG).

## Troubleshooting

### Tkinter not found

If you get tkinter errors, ensure the snap is using the bundled Python:
```bash
snap info nimbus-backup
```

### Permission denied errors

Grant necessary permissions:
```bash
sudo snap connect nimbus-backup:home
sudo snap connect nimbus-backup:network
sudo snap connect nimbus-backup:removable-media
```

### Google Drive authentication

The snap uses a confined environment. Place credentials at:
```
$HOME/snap/nimbus-backup/current/.nimbus/credentials.json
```

## Development

### Clean build

```bash
snapcraft clean
snapcraft
```

### Build for specific architecture

```bash
snapcraft --target-arch=amd64
snapcraft --target-arch=arm64
```

## Uninstall

```bash
sudo snap remove nimbus-backup
```

To remove all data:
```bash
sudo snap remove nimbus-backup --purge
```
