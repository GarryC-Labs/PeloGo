# 🏃🏻🚴🏻 PeloGo - Web UI (Flask - Python)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Windows | macOS | Linux](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg)](https://github.com)
[![macOS / Linux: Production Ready](https://img.shields.io/badge/macOS%20%2F%20Linux-Production%20Ready-brightgreen.svg)](https://github.com)
[![Windows: Testing](https://img.shields.io/badge/Windows-Testing-yellow.svg)](https://github.com)

A modern, web-based interface for managing Android fitness devices (Peloton Bike+, Tread etc). Install apps, manage settings, and control your fitness equipment from any browser.

## Features

✨ **Modern Web Interface**
- Beautiful, responsive UI built with the Flask Python Framework combined with TailwindCSS for styling. 
- Real-time device detection
- Intuitive app management

📦 **App Management**
- Browse curated app library
- One-click installation
- Installed app tracking
- Quick uninstall functionality

⚙️ **Device Control**
- Screen rotation management
- Default launcher switching
- Stay-awake settings
- Device information display

🔌 **Connection Methods**
- USB connections
- Automatic device discovery

📊 **Real-time Updates**
- WebSocket-powered log streaming
- Live installation progress
- Status notifications

## Installation

### Quick Start (Recommended)

**For Windows Devices:**
1. Download PeloGo
2. Double-click `setup.bat`
3. Follow prompts (auto-installs Python dependencies)
4. Open browser to `http://localhost:5004`

**For MacOS / Linux:**
1. Download PeloGo
2. Open Terminal in the pelogo folder
3. Run: `chmod +x setup.sh && ./setup.sh`
4. Follow prompts
5. Open browser to `http://localhost:5004`

### Prerequisites

The setup scripts require:
- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **ADB (Android Debug Bridge)** ([Download Platform Tools](https://developer.android.com/studio/releases/platform-tools))

The setup script will check for these and guide you through installation if needed.

### Manual Setup (Advanced)

```bash
# Create virtual environment
python3 -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# Install dependencies  
pip install -r requirements.txt

# Start server
python app.py
```

Then open: **http://localhost:5004**

## Device Setup

### ⚠️ Disclaimer - Use at Your Own Risk

**PeloGo was developed for personal use and development purposes only.** This is not an official tool and comes with no warranty. Device modifications are performed at your own risk. While all changes made with PeloGo are designed to be reversible, users assume full responsibility for any issues that may occur. See "Reversibility & Factory Reset" section below for restoration instructions.

### Enable USB Debugging

1. Go to **Settings → About Phone**
2. Tap **Build Number** 7 times to enable Developer Options
3. Go to **Settings → Developer Options**
4. Enable **USB Debugging**
5. Connect via USB cable and authorize the connection

## Usage Guide

### Getting Started Workflow

**If choosing to use PeloGo, the following steps can be performed once PeloGo is running and device is connected via USB:**

1. **Connect Device**
   - Connect Peloton device to PC/Mac/Linux via USB cable
   - Authorize the connection on the device when prompted

2. **Detect Device in PeloGo**
   - Open browser to `http://localhost:5004`
   - Click the **"Refresh Devices"** button in the top-right
   - Device should appear in the **Device Selector dropdown** (may take ~1 minute)
   - Select it to view device info and available options

3. **Install Apps** (Optional)
   - Browse app library or use search function
   - Select apps by clicking checkboxes
   - Click **"Install Selected"** to begin installation
   - Monitor Activity Log for installation status

4. **Manage Settings** (Optional)
   - **Screen Rotation**: Adjust via Settings panel
   - **Stay Awake**: Enable to prevent device sleep
   - **Launcher**: Switch home screen apps if available

5. **Disable Peloton Restrictions** (Optional - At Own Risk)
   - Scroll to **Advanced Options** section
   - Click **"Disable Restrictions"** button
   - Monitor Activity Log for confirmation
   - Device will unlock to full Android access

6. **Monitor & Manage**
   - Use **"View Installed"** to see installed apps and uninstall as needed
   - Check Activity Log for any errors or status updates
   - Click **"Re-lock Device"** to restore Peloton restrictions anytime

**💡 Note:** Changes are designed to be reversible. Use Activity Log to monitor device activity. Users assume full responsibility for any issues.

### Installing Apps

1. **Select Device**: Choose your connected device from the dropdown
2. **Browse Apps**: Scroll through the curated app library
3. **Search**: Use the search box to find specific apps
4. **Select Apps**: Check the boxes for apps you want to install
5. **Install**: Click "Install Selected" and watch the progress

### Managing Settings

1. **Screen Rotation**: Choose portrait, landscape, or reverse orientations
2. **Stay Awake**: Enable to prevent device from sleeping
3. **Launcher**: Switch between installed launcher apps (if available)

### Viewing Installed Apps

1. Click "View Installed" to see all third-party apps
2. Hover over an app to see the uninstall button
3. Click uninstall to remove an app

### Monitoring Activity

The Activity Log at the bottom shows real-time updates:
- Device connections/disconnections
- Installation progress
- Errors and warnings
- Settings changes

## Project Structure

```
pelogo/
├── app.py                    # Flask application (main server)
├── adb_service.py           # ADB wrapper & device control
├── requirements.txt         # Python dependencies
├── .env.example            # Configuration template
├── templates/
│   └── index.html          # Web UI (TailwindCSS + inline JS)
└── env/                    # Virtual environment
```

## API Endpoints

### Devices
- `GET /api/devices` - List connected devices
- `GET /api/devices/<serial>` - Get device details

### Apps
- `GET /api/apps` - List available apps
- `GET /api/devices/<serial>/apps/installed` - List installed apps
- `POST /api/devices/<serial>/apps/install` - Install app
- `DELETE /api/devices/<serial>/apps/<package>` - Uninstall app

### Settings
- `GET /api/devices/<serial>/settings/rotation` - Get rotation
- `PUT /api/devices/<serial>/settings/rotation` - Set rotation
- `POST /api/devices/<serial>/settings/stay-awake` - Enable stay awake
- `GET /api/devices/<serial>/launchers` - List launchers
- `POST /api/devices/<serial>/launchers/<component>` - Set launcher

### Logging
- `GET /api/logs` - Get all logs
- `POST /api/logs/clear` - Clear logs

### WebSocket
- Connect to `/socket.io/` for real-time updates

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Edit `.env`:
```
FLASK_ENV=development
FLASK_DEBUG=True
HOST=0.0.0.0
PORT=5004
ADB_TIMEOUT=30
```

### App Library

Apps are loaded from a local configuration file in the PeloGo directory:
```
./apps_config.json
```

**⚠️ App Testing Disclaimer:** The apps listed in `apps_config.json` have not been comprehensively tested on all device configurations. Users who choose to install applications do so entirely at their own risk. While the library includes popular applications, compatibility and device stability cannot be guaranteed. Test applications before relying on them for important functions. If issues occur, device restoration via factory reset is available (see "Reversibility & Factory Reset" section).

To customize or add new apps:

1. See **[APPS_CONFIG_GUIDE.md](APPS_CONFIG_GUIDE.md)** for detailed instructions
2. Edit `apps_config.json` in the PeloGo root directory to add/update apps
3. Restart the Flask server
4. Apps will be filtered by device architecture (ABI: `arm64-v8a` or `armeabi-v7a`)

## Troubleshooting

### "ADB not found in PATH"

**Problem**: The server can't find the ADB executable.

**Solution**:
1. Download [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools)
2. Extract to a location (e.g., `~/android-platform-tools`)
3. Add to PATH:
   - **macOS/Linux**: Add to `~/.zshrc` or `~/.bashrc`:
     ```bash
     export PATH="/path/to/platform-tools:$PATH"
     ```
   - **Windows**: Add to System Environment Variables

4. Verify: `adb version`

### "No devices found"

**Problem**: Connected device not showing up.

**Causes & Solutions**:
1. **USB Cable**: Try a different cable (data cables, not charging-only)
2. **USB Debugging**: Verify it's enabled in Developer Options
3. **USB Driver**: On Windows, install appropriate USB driver
4. **Authorization**: Accept the authorization prompt on the device
5. **Restart**: Restart ADB daemon: `adb kill-server && adb devices`

### "Installation failed"

**Problem**: App installation fails.

**Causes & Solutions**:
1. **Storage**: Device may be out of storage space
2. **Compatibility**: App may not support device architecture
3. **Network**: Internet connection may have dropped
4. **Device Lock**: Unlock device during installation
5. **Retry**: Try installing again

### "Cannot connect to server"

**Problem**: Browser can't reach http://localhost:5004

**Solutions**:
1. Verify server is running: Check console output
2. Check port: Is 5004 already in use? Change in `app.py`
3. Firewall: Allow Flask in firewall settings
4. Try: `http://127.0.0.1:5004` instead of `localhost`

### WebSocket connection fails

**Problem**: Real-time logs not updating.

**Solutions**:
1. Check browser console (F12) for errors
2. Ensure Flask-SocketIO is installed: `pip install flask-socketio`
3. Try different browser (Chrome, Firefox)
4. Disable browser extensions

## Development

### Running in Debug Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

The app will auto-reload on code changes.

### Adding New Features

1. **Backend endpoint**: Add route in `app.py`
2. **Frontend**: Update `templates/index.html`
3. **ADB functionality**: Add method to `adb_service.py`
4. **Styling**: TailwindCSS classes (CDN currently used)

### Testing

Test endpoints with curl:

```bash
# Get devices
curl http://localhost:5004/api/devices

# Get apps
curl http://localhost:5004/api/apps

# Install app (example)
curl -X POST http://localhost:5004/api/devices/SERIAL/apps/install \
  -H "Content-Type: application/json" \
  -d '{"app_name": "SmartSpin2k", "app_url": "..."}'
```

## Installation Method

PeloGo uses simple setup scripts for both Windows and macOS/Linux. Everything is straightforward - just run the setup script and you're done!

**All users should use:**
- Windows: `setup.bat`
- macOS/Linux: `setup.sh`

## Architecture

### Backend (Python/Flask)

- **app.py**: Main Flask application with REST API
- **adb_service.py**: Python wrapper around ADB commands
- **WebSocket**: Real-time log streaming to clients

### Frontend (HTML/CSS/JavaScript)

- **TailwindCSS**: Responsive, modern styling (CDN)
- **Feather Icons**: Beautiful icon library
- **Socket.io**: Real-time communication
- **Vanilla JavaScript**: No frameworks, lightweight

### Device Communication

```
Browser → Flask Server → ADB Service → ADB Binary → Android Device
```

## Performance

- **Response time**: <100ms for most endpoints
- **App installation**: 10-60 seconds (device-dependent)
- **Concurrent users**: Supports multiple browsers
- **Real-time logs**: WebSocket streaming (low latency)

## Security Notes

⚠️ **Local Network Only**: By default, runs on localhost only - perfect for personal use.

PeloGo is designed for local device management on your home network. It requires direct USB access to Android devices.

### Reversibility & Factory Reset

**Device modifications are designed to be reversible.** If restoration to original factory state is desired:

1. Go to **Settings → System → Reset Options**
2. Select **Erase all data (factory reset)**
3. Confirm the action
4. Device will reboot and restore to factory settings
5. Once complete, device returns to original state (for Peloton devices, Peloton app and restrictions are restored)

**Factory Reset Restores:**
- ✅ All apps installed via PeloGo are removed
- ✅ Device restrictions are re-enabled
- ✅ Device returns to original Peloton configuration
- ✅ All software modifications are reversed

**Important:** Factory reset erases all personal device data (similar to a full backup/restore). Back up important data before proceeding.
## Contributing

Contributions welcome! Areas for improvement:

- Additional device management features
- UI/UX improvements
- Performance optimizations
- Documentation
- Testing

## License

MIT License - See LICENSE file

## Support

### Issues

1. Check troubleshooting section above
2. Enable debug mode: `export FLASK_DEBUG=True`
3. Check console output for error messages

### Documentation

- [ADB Documentation](https://developer.android.com/studio/command-line/adb)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [TailwindCSS Documentation](https://tailwindcss.com/)

### Links

- **Original PeloGo**: https://github.com/doudar/pelogo
- **Android Platform Tools**: https://developer.android.com/studio/releases/platform-tools
- **SmartSpin2k**: https://github.com/doudar/SmartSpin2k

## Security Note

This application only downloads apps from trusted sources specified in the configuration file. However, users should always be cautious when installing third-party applications on their devices. Ensure you understand what each application does before installation, and only install apps from verified sources.

## Disclaimer

**PeloGo** is an independent, open-source project and is not affiliated with, associated with, authorized by, endorsed by, or in any way officially connected with Peloton Interactive, Inc., or any of its subsidiaries or affiliates. The official Peloton website can be found at https://www.onepeloton.com.

All product and company names including but not limited to "Peloton" are trademarks or registered trademarks of their respective holders. This tool is provided for educational and experimental purposes only. Use of PeloGo is at your own risk; the developers assume no liability for any damage to your device, voiding of warranties, or other issues that may result from its use.

### Important: At Your Own Risk Acknowledgment

**Modifications made with PeloGo are designed to be reversible** via factory reset. See the "Reversibility & Factory Reset" section above for restoration procedures. However, all use of this tool is entirely at the user's own risk.

By using this application, users acknowledge:
- Device ownership and full responsibility for any modifications
- Understanding of risks involved in enabling developer options and custom app installation
- Full liability acceptance for all consequences of using this application
- The developers assume no liability for device damage, data loss, or warranty issues
- Ability to reverse changes via factory reset if restoration is desired

---

**Built with ❤️ for fitness enthusiasts and Android developers**

Developed with support from [Claude AI](https://claude.ai)
