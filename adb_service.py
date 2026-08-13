"""
ADB Service - Python wrapper for Android Debug Bridge
Handles all device communication and management
"""
import subprocess
import os
import json
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import requests
from datetime import datetime
import tempfile
import platform


class AdbService:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback or (lambda msg, tag: None)
        self.adb_path = self._find_or_setup_adb()
        self.connected_ip = None
        self.connected_port = 5555

    def _find_or_setup_adb(self) -> str:
        """Find ADB binary in PATH"""
        try:
            result = subprocess.run(['adb', 'version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return 'adb'
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        raise RuntimeError(
            "ADB not found in PATH. Please install Android SDK Platform Tools:\n"
            "https://developer.android.com/studio/releases/platform-tools"
        )

    def log(self, message: str, tag: str = 'info'):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_callback(f"[{timestamp}] {message}", tag)

    def run_adb_command(self, args: List[str], timeout: int = 30) -> Tuple[int, str, str]:
        """Execute ADB command and return (exit_code, stdout, stderr)"""
        cmd = [self.adb_path] + args
        self.log(f"$ adb {' '.join(args)}", 'command')

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if result.stdout.strip():
                self.log(result.stdout.strip(), 'stdout')
            if result.stderr.strip():
                self.log(result.stderr.strip(), 'stderr')
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            self.log(f"Command timed out after {timeout}s", 'error')
            return -1, "", "Timeout"
        except Exception as e:
            self.log(f"Command failed: {e}", 'error')
            return -1, "", str(e)

    def get_connected_devices(self) -> List[Dict]:
        """Get list of connected devices"""
        code, stdout, stderr = self.run_adb_command(['devices'])

        devices = []
        for line in stdout.split('\n')[1:]:  # Skip header
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) < 2:
                continue

            serial, status = parts[0], parts[1]
            if status != 'device':
                continue

            device = {
                'serial': serial,
                'status': status,
                'name': self._get_device_name(serial),
                'abi': self._get_device_abi(serial),
                'transport': 'wifi' if ':' in serial else 'usb',
                'model': self._get_device_model(serial),
            }
            devices.append(device)

        if devices:
            self.log(f"Found {len(devices)} device(s)", 'info')
        else:
            self.log("No devices found", 'warning')
        return devices

    def _get_device_name(self, serial: str) -> str:
        """Get device manufacturer and model"""
        try:
            _, manufacturer, _ = self.run_adb_command(
                ['-s', serial, 'shell', 'getprop', 'ro.product.manufacturer']
            )
            _, model, _ = self.run_adb_command(
                ['-s', serial, 'shell', 'getprop', 'ro.product.model']
            )
            name = f"{manufacturer.strip()} {model.strip()}".strip()
            return name if name else serial
        except Exception:
            return serial

    def _get_device_model(self, serial: str) -> str:
        """Get device model"""
        try:
            _, model, _ = self.run_adb_command(
                ['-s', serial, 'shell', 'getprop', 'ro.product.model']
            )
            return model.strip()
        except Exception:
            return "Unknown"

    def _get_device_abi(self, serial: str) -> str:
        """Get device ABI (arm64-v8a, armeabi-v7a, etc.)"""
        try:
            _, abi, _ = self.run_adb_command(
                ['-s', serial, 'shell', 'getprop', 'ro.product.cpu.abi']
            )
            return abi.strip()
        except Exception:
            return "unknown"

    def install_apk(self, serial: str, apk_path: str) -> bool:
        """Install APK on device with fallback flags"""
        self.log(f"Installing {Path(apk_path).name} to {serial}", 'info')

        if not os.path.exists(apk_path):
            self.log(f"APK not found: {apk_path}", 'error')
            return False

        install_attempts = [
            ['-r', '-d', '-g', '-t'],
            ['-r', '-g', '-t'],
            ['-r', '-t'],
            ['-r'],
        ]

        for flags in install_attempts:
            args = ['-s', serial, 'install'] + flags + [apk_path]
            code, stdout, stderr = self.run_adb_command(args, timeout=120)
            output = stdout + stderr

            if 'Success' in output:
                self.log("✓ Installation successful!", 'info')
                return True

            if 'Unknown option' in output:
                # Try with fewer flags
                continue

            # Other error, report it
            self.log(f"Installation attempt with {flags} failed: {output[:200]}", 'warning')

        self.log("All installation attempts failed", 'error')
        return False

    def uninstall_package(self, serial: str, package_name: str) -> bool:
        """Uninstall package from device"""
        self.log(f"Uninstalling {package_name} from {serial}", 'info')
        code, stdout, stderr = self.run_adb_command(['-s', serial, 'uninstall', package_name])
        success = code == 0 and 'Success' in (stdout + stderr)
        if success:
            self.log("✓ Uninstall successful!", 'info')
        return success

    def list_installed_packages(self, serial: str, include_system: bool = False) -> List[str]:
        """List installed packages on device"""
        cmd = ['pm', 'list', 'packages']
        if not include_system:
            cmd.append('-3')  # Only third-party apps

        code, stdout, stderr = self.run_adb_command(['-s', serial, 'shell'] + cmd)
        packages = []
        for line in stdout.split('\n'):
            line = line.strip()
            if line.startswith('package:'):
                packages.append(line.replace('package:', ''))
        return sorted(packages)

    def set_rotation(self, serial: str, rotation: int) -> bool:
        """Set device rotation (0-3)"""
        try:
            self.run_adb_command(
                ['-s', serial, 'shell', 'settings', 'put', 'system', 'accelerometer_rotation', '0']
            )
            code, _, _ = self.run_adb_command(
                ['-s', serial, 'shell', 'settings', 'put', 'system', 'user_rotation', str(rotation)]
            )
            if code == 0:
                rotation_names = {0: 'Portrait', 1: 'Landscape', 2: 'Reverse Portrait', 3: 'Reverse Landscape'}
                self.log(f"✓ Rotation set to {rotation_names.get(rotation, 'Unknown')}", 'info')
                return True
            return False
        except Exception as e:
            self.log(f"Error setting rotation: {e}", 'error')
            return False

    def get_rotation(self, serial: str) -> int:
        """Get current display rotation"""
        try:
            code, stdout, _ = self.run_adb_command(
                ['-s', serial, 'shell', 'settings', 'get', 'system', 'user_rotation']
            )
            return int(stdout.strip()) if stdout.strip() else 0
        except Exception:
            return 0

    def enable_stay_awake(self, serial: str) -> bool:
        """Enable stay awake while charging"""
        try:
            code, _, _ = self.run_adb_command(
                ['-s', serial, 'shell', 'settings', 'put', 'global', 'stay_on_while_plugged_in', '3']
            )
            if code == 0:
                self.log("✓ Stay awake enabled", 'info')
                return True
            return False
        except Exception as e:
            self.log(f"Error enabling stay awake: {e}", 'error')
            return False

    def download_and_install_apk(self, serial: str, app_url: str, app_name: str) -> bool:
        """Download APK from URL and install it"""
        try:
            self.log(f"Downloading {app_name}...", 'info')
            response = requests.get(app_url, timeout=300, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with tempfile.NamedTemporaryFile(suffix='.apk', delete=False) as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            self.log(f"Download progress: {percent}%", 'info')
                temp_path = f.name

            self.log(f"Download complete: {app_name}", 'info')

            # Install
            success = self.install_apk(serial, temp_path)

            # Cleanup
            try:
                os.unlink(temp_path)
            except Exception:
                pass

            return success

        except Exception as e:
            self.log(f"Download/install failed: {e}", 'error')
            return False

    def get_installed_launchers(self, serial: str) -> List[Dict[str, str]]:
        """Get installed launcher apps"""
        try:
            code, stdout, _ = self.run_adb_command([
                '-s', serial, 'shell', 'pm', 'query-activities',
                '--components', '-a', 'android.intent.action.MAIN',
                '-c', 'android.intent.category.HOME'
            ])

            launchers = []
            seen_components = set()

            for line in stdout.split('\n'):
                line = line.strip()
                if not line:
                    continue
                component = self._extract_component_from_line(line)
                if component and component not in seen_components:
                    seen_components.add(component)
                    pkg = component.split('/')[0]
                    if pkg:
                        label = self._get_app_label(serial, pkg)
                        launchers.append({
                            'package': pkg,
                            'component': component,
                            'label': label if label else pkg,
                        })

            return launchers if launchers else []
        except Exception as e:
            self.log(f"Error listing launchers: {e}", 'error')
            return []

    def set_default_launcher(self, serial: str, component: str) -> bool:
        """Set default HOME activity"""
        try:
            code, _, stderr = self.run_adb_command([
                '-s', serial, 'shell', 'cmd', 'package', 'set-home-activity', component
            ])
            if code == 0:
                self.log(f"✓ Default launcher set", 'info')
                return True
            self.log(f"Failed to set launcher: {stderr}", 'error')
            return False
        except Exception as e:
            self.log(f"Error setting launcher: {e}", 'error')
            return False

    def get_default_launcher_component(self, serial: str) -> Optional[str]:
        """Get currently resolved default launcher"""
        try:
            code, stdout, _ = self.run_adb_command([
                '-s', serial, 'shell', 'cmd', 'package', 'resolve-activity',
                '--brief', '-a', 'android.intent.action.MAIN',
                '-c', 'android.intent.category.HOME'
            ])

            for line in stdout.split('\n'):
                line = line.strip()
                if line:
                    component = self._extract_component_from_line(line)
                    if component:
                        return component
            return None
        except Exception as e:
            self.log(f"Error getting current launcher: {e}", 'error')
            return None

    def _extract_component_from_line(self, line: str) -> Optional[str]:
        """Extract component from pm output line"""
        import re
        match = re.search(r'([A-Za-z0-9_.$]+/[A-Za-z0-9_.$]+)', line)
        return match.group(1) if match else None

    def _get_app_label(self, serial: str, package: str) -> Optional[str]:
        """Get friendly app label for package"""
        try:
            code, stdout, _ = self.run_adb_command([
                '-s', serial, 'shell', 'dumpsys', 'package', package
            ])
            import re
            match = re.search(r'label[=:]([^\n]+)', stdout, re.IGNORECASE)
            if match:
                label = match.group(1).strip()
                if label and not label.startswith('0x'):
                    return label
            return None
        except Exception:
            return None

    def take_screenshot(self, serial: str, local_path: str) -> bool:
        """Capture screenshot from device"""
        try:
            remote_path = '/sdcard/screenshot.png'
            self.log("Taking screenshot...", 'info')
            self.run_adb_command(['-s', serial, 'shell', 'screencap', '-p', remote_path])
            self.log("Downloading screenshot...", 'info')
            code, _, _ = self.run_adb_command(['-s', serial, 'pull', remote_path, local_path])
            if code == 0:
                self.run_adb_command(['-s', serial, 'shell', 'rm', remote_path])
                self.log(f"✓ Screenshot saved", 'info')
                return True
            return False
        except Exception as e:
            self.log(f"Screenshot failed: {e}", 'error')
            return False

    def disable_peloton_restrictions(self, serial: str) -> Dict[str, bool]:
        """Disable Peloton system restrictions (systempluginui)"""
        self.log("🔓 Disabling Peloton restrictions...", 'info')
        results = {}

        try:
            # Disable the main system plugin that enforces restrictions
            code, stdout, stderr = self.run_adb_command([
                '-s', serial, 'shell', 'pm', 'disable-user', '--user', '0',
                'com.onepeloton.systempluginui'
            ])
            success = code == 0
            results['disable_system_plugin'] = success
            if success:
                self.log("✓ Peloton system restrictions disabled", 'info')
            else:
                self.log(f"⚠️ Could not disable system plugin: {stderr}", 'warning')
        except Exception as e:
            self.log(f"Error disabling restrictions: {e}", 'error')
            results['disable_system_plugin'] = False

        return results

    def enable_peloton_restrictions(self, serial: str) -> Dict[str, bool]:
        """Re-enable Peloton system restrictions (systempluginui)"""
        self.log("🔒 Re-enabling Peloton restrictions...", 'info')
        results = {}

        try:
            code, stdout, stderr = self.run_adb_command([
                '-s', serial, 'shell', 'pm', 'enable', '--user', '0',
                'com.onepeloton.systempluginui'
            ])
            success = code == 0
            results['enable_system_plugin'] = success
            if success:
                self.log("✓ Peloton system restrictions re-enabled", 'info')
            else:
                self.log(f"⚠️ Could not enable system plugin: {stderr}", 'warning')
        except Exception as e:
            self.log(f"Error enabling restrictions: {e}", 'error')
            results['enable_system_plugin'] = False

        return results
