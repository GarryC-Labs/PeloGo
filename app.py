"""
PeloGo Web - Flask Application
Modern web-based interface for managing Android devices
"""
import json
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime
from pathlib import Path
import os
import sys

from adb_service import AdbService

# ============================================================================
# Flask Application Setup
# ============================================================================

app = Flask(__name__, template_folder='templates')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
adb_service = None
connected_clients = set()
config = {}


# ============================================================================
# Logging System - Stream to WebSocket Clients
# ============================================================================

class LogCapture:
    def __init__(self):
        self.logs = []
        self.max_logs = 500

    def add_log(self, message: str, tag: str = 'info'):
        """Add log entry and broadcast to WebSocket clients"""
        entry = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'message': message,
            'tag': tag
        }
        self.logs.append(entry)

        # Keep only last N logs
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]

        # Broadcast to all connected WebSocket clients (only if clients exist)
        if connected_clients:
            try:
                socketio.emit('log', entry, broadcast=True)
            except Exception:
                # Ignore emit errors (e.g., during initialization)
                pass

        # Print to console as well
        print(f"[{entry['timestamp']}] {message}")

    def get_logs(self):
        return self.logs

    def clear(self):
        self.logs = []


log_capture = LogCapture()


# ============================================================================
# Configuration Loading
# ============================================================================

def load_config():
    """Load apps configuration from JSON"""
    global config
    try:
        config_path = Path(__file__).parent / 'apps_config.json'
        if not config_path.exists():
            log_capture.add_log(f"Config not found at {config_path}", 'warning')
            config = {"apps": {}}
            return

        with open(config_path) as f:
            config = json.load(f)
        log_capture.add_log(f"Loaded {len(config.get('apps', {}))} apps from config", 'info')
    except Exception as e:
        log_capture.add_log(f"Error loading config: {e}", 'error')
        config = {"apps": {}}


# ============================================================================
# REST API Routes
# ============================================================================

@app.route('/')
def index():
    """Serve main HTML page"""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get list of connected devices"""
    try:
        devices = adb_service.get_connected_devices()
        return jsonify({'success': True, 'devices': devices, 'count': len(devices)})
    except Exception as e:
        log_capture.add_log(f"Error getting devices: {e}", 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/devices/<serial>', methods=['GET'])
def get_device_info(serial: str):
    """Get detailed info about a specific device"""
    try:
        devices = adb_service.get_connected_devices()
        device = next((d for d in devices if d['serial'] == serial), None)
        if device:
            return jsonify({'success': True, 'device': device})
        return jsonify({'success': False, 'error': 'Device not found'}), 404
    except Exception as e:
        log_capture.add_log(f"Error getting device info: {e}", 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/apps', methods=['GET'])
def get_apps():
    """Get available apps from config"""
    try:
        apps = []
        for app_name, app_info in config.get('apps', {}).items():
            apps.append({
                'name': app_name,
                'url': app_info.get('url', ''),
                'package_name': app_info.get('package_name', ''),
                'description': app_info.get('description', ''),
                'abi': app_info.get('abi', 'arm64-v8a')
            })

        # Filter by ABI if requested
        abi_filter = request.args.get('abi')
        if abi_filter:
            apps = [app for app in apps if app['abi'] == abi_filter or abi_filter == 'all']

        return jsonify({'success': True, 'apps': apps, 'count': len(apps)})
    except Exception as e:
        log_capture.add_log(f"Error loading apps: {e}", 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/devices/<serial>/apps/installed', methods=['GET'])
def get_installed_apps(serial: str):
    """Get installed apps on device"""
    try:
        include_system = request.args.get('system', 'false').lower() == 'true'
        packages = adb_service.list_installed_packages(serial, include_system=include_system)
        return jsonify({'success': True, 'packages': packages, 'count': len(packages)})
    except Exception as e:
        log_capture.add_log(f"Error listing apps: {e}", 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/devices/<serial>/apps/install', methods=['POST'])
def install_app(serial: str):
    """Install app on device"""
    try:
        data = request.json
        app_name = data.get('app_name')
        app_url = data.get('app_url')

        if not app_name or not app_url:
            return jsonify({'success': False, 'error': 'Missing app_name or app_url'}), 400

        log_capture.add_log(f"🚀 Starting installation of {app_name} on {serial}", 'info')

        success = adb_service.download_and_install_apk(serial, app_url, app_name)

        if success:
            msg = f"✅ {app_name} installed successfully!"
            log_capture.add_log(msg, 'info')
            return jsonify({'success': True, 'message': msg})
        else:
            msg = f"❌ Failed to install {app_name}"
            log_capture.add_log(msg, 'error')
            return jsonify({'success': False, 'message': msg}), 400

    except Exception as e:
        error_msg = f"Installation error: {e}"
        log_capture.add_log(error_msg, 'error')
        return jsonify({'success': False, 'error': error_msg}), 500


@app.route('/api/devices/<serial>/apps/<package_name>', methods=['DELETE'])
def uninstall_app(serial: str, package_name: str):
    """Uninstall app from device"""
    try:
        log_capture.add_log(f"Uninstalling {package_name}...", 'info')
        success = adb_service.uninstall_package(serial, package_name)
        if success:
            msg = f"✅ {package_name} uninstalled"
            log_capture.add_log(msg, 'info')
            return jsonify({'success': True, 'message': msg})
        else:
            msg = f"❌ Uninstall failed"
            log_capture.add_log(msg, 'error')
            return jsonify({'success': False, 'message': msg}), 400
    except Exception as e:
        log_capture.add_log(f"Uninstall error: {e}", 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/devices/<serial>/settings/rotation', methods=['GET', 'PUT'])
def device_rotation(serial: str):
    """Get/Set device rotation"""
    try:
        if request.method == 'GET':
            rotation = adb_service.get_rotation(serial)
            return jsonify({'success': True, 'rotation': rotation})
        else:
            data = request.json
            rotation = data.get('rotation', 0)
            success = adb_service.set_rotation(serial, int(rotation))
            if success:
                return jsonify({'success': True, 'message': 'Rotation updated'})
            else:
                return jsonify({'success': False, 'message': 'Failed to set rotation'}), 400
    except Exception as e:
        log_capture.add_log(f"Rotation error: {e}", 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/devices/<serial>/settings/stay-awake', methods=['POST'])
def enable_stay_awake(serial: str):
    """Enable stay awake while charging"""
    try:
        success = adb_service.enable_stay_awake(serial)
        if success:
            return jsonify({'success': True, 'message': 'Stay awake enabled'})
        else:
            return jsonify({'success': False, 'message': 'Failed to enable stay awake'}), 400
    except Exception as e:
        log_capture.add_log(f"Stay awake error: {e}", 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/devices/<serial>/launchers', methods=['GET'])
def get_launchers(serial: str):
    """Get available launcher apps"""
    try:
        launchers = adb_service.get_installed_launchers(serial)
        current = adb_service.get_default_launcher_component(serial)
        return jsonify({
            'success': True,
            'launchers': launchers,
            'current': current
        })
    except Exception as e:
        log_capture.add_log(f"Error getting launchers: {e}", 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/devices/<serial>/launchers/<component>', methods=['POST'])
def set_launcher(serial: str, component: str):
    """Set default launcher"""
    try:
        # URL decode the component
        import urllib.parse
        component = urllib.parse.unquote(component)
        success = adb_service.set_default_launcher(serial, component)
        if success:
            return jsonify({'success': True, 'message': 'Launcher updated'})
        else:
            return jsonify({'success': False, 'message': 'Failed to set launcher'}), 400
    except Exception as e:
        log_capture.add_log(f"Launcher error: {e}", 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get all logs"""
    limit = request.args.get('limit', 100, type=int)
    logs = log_capture.get_logs()[-limit:]
    return jsonify({'success': True, 'logs': logs})


@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """Clear logs"""
    log_capture.clear()
    return jsonify({'success': True})


@app.route('/api/devices/<serial>/peloton/disable-restrictions', methods=['POST'])
def disable_peloton_restrictions(serial: str):
    """Disable Peloton system restrictions"""
    try:
        results = adb_service.disable_peloton_restrictions(serial)
        if results.get('disable_system_plugin'):
            return jsonify({'success': True, 'message': 'Peloton restrictions disabled', 'results': results})
        else:
            return jsonify({'success': False, 'message': 'Failed to disable restrictions', 'results': results}), 400
    except Exception as e:
        log_capture.add_log(f"Error disabling restrictions: {e}", 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/devices/<serial>/peloton/enable-restrictions', methods=['POST'])
def enable_peloton_restrictions(serial: str):
    """Re-enable Peloton system restrictions"""
    try:
        results = adb_service.enable_peloton_restrictions(serial)
        if results.get('enable_system_plugin'):
            return jsonify({'success': True, 'message': 'Peloton restrictions re-enabled', 'results': results})
        else:
            return jsonify({'success': False, 'message': 'Failed to enable restrictions', 'results': results}), 400
    except Exception as e:
        log_capture.add_log(f"Error enabling restrictions: {e}", 'error')
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# WebSocket Events
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Client connected to WebSocket"""
    connected_clients.add(request.sid)
    emit('status', {'data': 'Connected to server', 'clients': len(connected_clients)})
    print(f"Client connected: {request.sid} (total: {len(connected_clients)})")


@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected from WebSocket"""
    connected_clients.discard(request.sid)
    print(f"Client disconnected: {request.sid} (total: {len(connected_clients)})")


@socketio.on('request_devices')
def handle_devices_request():
    """Client requests device list"""
    try:
        devices = adb_service.get_connected_devices()
        emit('devices_update', {'devices': devices})
    except Exception as e:
        emit('error', {'message': str(e)})


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'success': False, 'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


# ============================================================================
# Initialization
# ============================================================================

def initialize():
    """Initialize the application"""
    global adb_service

    log_capture.add_log("=" * 60, 'info')
    log_capture.add_log("🏋️  PeloGo Web Server Starting", 'info')
    log_capture.add_log("=" * 60, 'info')

    try:
        # Initialize ADB service
        adb_service = AdbService(log_callback=log_capture.add_log)
        log_capture.add_log("✓ ADB Service initialized", 'info')

        # Load configuration
        load_config()

        # Log startup info
        log_capture.add_log(f"Python {sys.version.split()[0]}", 'info')
        log_capture.add_log(f"Platform: {sys.platform}", 'info')
        log_capture.add_log("Server ready for connections", 'info')
        log_capture.add_log("=" * 60, 'info')

    except Exception as e:
        log_capture.add_log(f"❌ Initialization error: {e}", 'error')
        raise


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == '__main__':
    initialize()

    print("\n" + "=" * 60)
    print("🚀 PeloGo Web Server")
    print("=" * 60)
    print("📱 Open your browser and navigate to:")
    print("   http://localhost:5004")
    print("=" * 60 + "\n")

    socketio.run(
        app,
        host='0.0.0.0',
        port=5004,
        debug=True,
        use_reloader=True
    )
