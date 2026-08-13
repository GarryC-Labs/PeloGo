# Peloton Device Restrictions & How to Bypass Them

## Overview

This guide explains Peloton device software restrictions and how they function. It is provided for educational and personal development purposes only. This guide was developed for individual use and experimentation.

**⚠️ Disclaimer:** Device modifications are performed entirely at your own risk. This guide comes with no warranty. Device owners modifying their own equipment assume full responsibility for any issues that may occur. In most jurisdictions, device owners have rights to modify software on devices they own for personal use, but local laws vary—verify your local regulations before proceeding. Device modifications may void your Peloton warranty.

---

## Peloton-Related Apps on Your Device

### 1. **com.onepeloton.bachman** ⭐ IMPORTANT
- **Purpose:** Peloton's custom launcher and home screen
- **What it does:** Replaces Android's default home screen with Peloton's interface
- **Restriction:** Forces device to only show Peloton apps
- **Can disable:** Yes (using an alternative launcher like Lawnchair)
- **Impact:** Allows access to full Android home screen and other apps

### 2. **com.onepeloton.odyssey**
- **Purpose:** Peloton workout/content service
- **What it does:** Core Peloton workout app and service
- **Restriction:** Moderate - requires Peloton app for workouts
- **Can disable:** Not recommended (core functionality)
- **Impact:** Disabling removes Peloton workout capability

### 3. **com.onepeloton.sensor.diagnostics**
- **Purpose:** Bike/Tread sensor monitoring
- **What it does:** Communicates with bike sensors (resistance, cadence, etc.)
- **Restriction:** Minor
- **Can disable:** Not recommended (loses sensor functionality)
- **Impact:** Bike sensors won't work without this

### 4. **com.onepeloton.workoutservices.app**
- **Purpose:** Workout data and services
- **What it does:** Handles workout tracking and data sync
- **Restriction:** None
- **Can disable:** Yes (if you don't care about Peloton tracking)
- **Impact:** Disables workout data syncing to Peloton
- **Note:** You can re-enable this anytime via PeloGo's "Re-lock Device" button

### 5. **com.onepeloton.systempluginui** ⭐⭐⭐ THE KEY ONE
- **Purpose:** System-level app enforcer
- **What it does:** Prevents access to non-Peloton apps, enforces restrictions
- **Restriction:** MAXIMUM - This is what locks you into Peloton ecosystem
- **Can disable:** YES! This is the main unlock
- **Impact:** HUGE - Allows full device freedom, other apps accessible

---

## The Peloton Lockdown Explained

### How Peloton Restricts Your Device

```
1. Peloton OEM Cleanup Plugin (systempluginui)
   ↓
   Monitors which apps can run
   ↓
2. Forces Peloton Launcher (bachman)
   ↓
   Controls what home screen shows
   ↓
3. Result: Device only accessible through Peloton ecosystem
```

### Why Peloton Does This

- **Keeps users in ecosystem** - All content goes through Peloton
- **Prevents "unauthorized" apps** - No competing fitness apps
- **Monetization** - Forces use of Peloton content
- **Control** - Prevents users from sideloading or modifying

---

## How to Bypass Peloton Restrictions

### THE SOLUTION: Disable the System Plugin UI

The main restriction enforcer is **com.onepeloton.systempluginui**. By disabling this, you regain full device control.

#### Method 1: Using ADB (Recommended)

```bash
# Via PeloGo or command line:
adb -s <device-serial> shell pm disable-user --user 0 com.onepeloton.systempluginui

# Verify it's disabled:
adb -s <device-serial> shell pm list packages -d com.onepeloton.systempluginui
```

**Expected output:** Should show the package as disabled.

#### Method 2: Using PeloGo (Personal Development Tool)

PeloGo offers automated options for:
- ✅ Disable Peloton System Plugin
- ✅ Enable alternative launchers
- ✅ Re-lock device to restore restrictions
- These options are accessible in the "Advanced Options" section of the PeloGo web interface

---

## What Happens When systempluginui is Disabled

### ✅ Device Gains Access To:
1. **Full Android Home Screen** - Install and use any launcher
2. **Third-Party Apps** - Zwift, Spotify, YouTube, Netflix, etc.
3. **System Settings** - Full control over device behavior
4. **Alternative Launchers** - Lawnchair, Nova, KISS, etc.
5. **Custom ROMs** - Advanced users can go further

### ⚠️ Device Loses Access To:
1. **Peloton Workouts** - Will not launch properly from Peloton app
2. **Peloton Content** - Restricted to Peloton ecosystem
3. **Built-in Lockdown** - Device becomes fully open/unrestricted

**Tradeoff:** Device gains full app access but loses tight Peloton integration

**Reversible:** The restrictions can be easily restored anytime by clicking **"Re-lock Device"** in the Advanced Options section of the PeloGo web interface. This will restore the Peloton lockdown and all original restrictions.

---

## Step-by-Step Removal Guide

### Prerequisites
- Device connected via USB (or WiFi with ADB enabled)
- PeloGo or ADB installed on your computer
- Device with Developer Options enabled

### Full Unlock Process

#### Step 1: Connect Device
```bash
adb devices
# Should show your device as "device"
```

#### Step 2: Disable Peloton System Plugin
```bash
adb shell pm disable-user --user 0 com.onepeloton.systempluginui
```

Expected message: `java.lang.SecurityException: Unknown package: com.onepeloton.systempluginui`
OR: `Package com.onepeloton.systempluginui new state: disabled-user`

(Both mean it worked)

#### Step 3: Install Alternative Launcher
**Option A: Via ADB (if you have APK)**
```bash
adb install lawnchair.apk
# Or your preferred launcher
```

**Option B: Via App Store**
1. Open Play Store or Aurora Store
2. Search for "Lawnchair Launcher"
3. Install
4. Set as default launcher

#### Step 4: Test
1. Reboot device
2. Home screen should now show your new launcher
3. Install other apps and test them

---

## What Each App Does in Detail

### com.onepeloton.bachman
```
Peloton Launcher
├─ Replaces standard Android home
├─ Shows only Peloton-approved apps
├─ Restricts access to system menus
└─ Can be replaced with alternative launcher
```

**How to replace:**
1. Install Lawnchair or alternative launcher
2. Settings → Apps → Default apps → Home
3. Select new launcher
4. Can optionally uninstall Bachman after

### com.onepeloton.odyssey
```
Peloton Workout Service
├─ Main workout/content app
├─ Connects to Peloton account
├─ Streams workout content
├─ Not recommended to disable
└─ Core to Peloton functionality
```

**Don't disable** unless you don't want Peloton workouts.

### com.onepeloton.sensor.diagnostics
```
Sensor Communication
├─ Talks to bike/tread sensors
├─ Reads resistance, cadence, power
├─ Diagnostic monitoring
└─ Required for accurate metrics
```

**Don't disable** if you want sensor data.

### com.onepeloton.workoutservices.app
```
Workout Data Service
├─ Tracks workout stats
├─ Syncs to Peloton servers
├─ Not essential for basic use
└─ Can disable if you don't care about data sync
```

**Safe to disable** if you're not uploading to Peloton.

### com.onepeloton.systempluginui ⭐⭐⭐
```
THE LOCKDOWN ENFORCER
├─ System-level app manager
├─ Prevents non-Peloton apps
├─ Blocks access to full Android
├─ THIS is what you need to disable
└─ Disabling gives you freedom
```

**THIS IS THE KEY.** Disable this and everything opens up.

---

## Reverting Changes (How to Re-Lock)

If you want to go back to Peloton's lockdown:

```bash
# Re-enable the system plugin
adb shell pm enable --user 0 com.onepeloton.systempluginui

# Reboot device
adb reboot
```

---

## Troubleshooting

### "Package not found" error
```bash
# Verify package exists:
adb shell pm list packages | grep onepeloton
# Should show multiple peloton packages
```

### Device won't respond to ADB commands
```bash
# Kill and restart ADB daemon
adb kill-server
adb devices
# Try commands again
```

### Settings app won't open
- This is normal - Peloton blocks it
- Once systempluginui is disabled, should work

### Can't install new launcher
- Verify systempluginui is actually disabled
- Verify package manager enabled
- Try installing via Play Store instead of ADB

---

## Advanced Options

### Option 1: Keep Everything, Just App Freedom
- Only disable systempluginui
- Keep Peloton ecosystem intact
- Access streaming and third-party apps directly
- **Best option for most users**

### Option 2: Full Android Freedom
- Disable systempluginui
- Install Lawnchair launcher
- Remove Peloton launcher (optional)
- Install alternative apps
- **Most flexible but loses tight integration**

### Option 3: Hybrid Setup
- Disable systempluginui
- Install launcher switcher
- Keep Peloton for workouts
- Use other apps for entertainment
- **Best of both worlds**

---

## FAQ

**Q: Will disabling these apps break my bike/tread?**
A: No. The physical hardware is separate. Only software changes occur.

**Q: Can I uninstall instead of disable?**
A: No, you cannot uninstall system apps. Disable is the safe option.

**Q: Will updates re-enable these restrictions?**
A: Possibly. Keep documentation of what you disabled in case you need to re-disable after update.

**Q: Is this permanent?**
A: No, you can re-enable at any time with the reverting commands.

**Q: Will Peloton know I did this?**
A: They won't be notified automatically, but if you contact support, they may see it in device logs.

**Q: Can I still do Peloton workouts?**
A: Yes, the Peloton app still works. You just have more freedom with other apps too.

**Q: What about warranty?**
A: Depends on your warranty terms. This is non-destructive software modification. Keep receipts.

---

## Safety Notes

### ✅ SAFE TO DO:
- Disable system plugins
- Install alternative launchers
- Install third-party apps
- Configure app permissions
- Use PeloGo to manage restrictions

### ⚠️ PROCEED WITH CAUTION:
- Uninstalling core Peloton services
- Modifying system partitions
- Installing custom ROMs (advanced)
- Removing hardware drivers

### ❌ DON'T DO:
- Delete system files
- Flash unsupported ROMs
- Remove sensor drivers
- Modify hardware

---

## Your Current Device Status

Based on your installed apps:
- ✅ Alternative launcher available (com.teslacoilsw.launcher - Nova)
- ✅ System plugin is ENABLED (restricting access)
- ⚠️ Still locked to Peloton ecosystem

### Recommended Next Steps:
1. Disable com.onepeloton.systempluginui via PeloGo
2. Set alternative launcher as default
3. Install and test third-party apps
4. Use PeloGo's "Re-lock Device" button anytime to restore restrictions

---

## Integration with PeloGo

PeloGo includes buttons in the "Advanced Options" section to:
- ✅ Disable Peloton restrictions with one click
- ✅ Re-lock device to restore restrictions anytime
- ✅ Switch between installed launchers
- ✅ Manage app installations

See the PeloGo README.md for complete feature documentation.

---

## Resources

### External Links
- [ADB Documentation](https://developer.android.com/studio/command-line/adb)
- [Android Developer Options](https://developer.android.com/studio/debug/dev-options)
- [Peloton Community Forums](https://www.reddit.com/r/pelotoncycle/)

### Related Tools
- PeloGo (this project)
- [SmartSpin2k](https://github.com/doudar/SmartSpin2k)
- [Lawnchair Launcher](https://github.com/LawnchairLauncher/lawnchair)

---

## Summary Table

| Package | Function | Restrict? | Disable? | Impact |
|---------|----------|-----------|----------|--------|
| **com.onepeloton.bachman** | Home launcher | HIGH | Yes | Full Android home access |
| **com.onepeloton.odyssey** | Workouts | MEDIUM | No | Keeps Peloton workouts |
| **com.onepeloton.sensor.diagnostics** | Sensors | LOW | No | Keeps bike metrics |
| **com.onepeloton.workoutservices.app** | Data sync | NONE | Yes | Stops data syncing |
| **com.onepeloton.systempluginui** | ENFORCER | MAX | YES ⭐ | FULL FREEDOM |

---

## Legal & Ethical

**You own your device.** Modifying software on devices you own is:
- ✅ Legal in most jurisdictions
- ✅ Your right as the owner
- ✅ Common practice
- ✅ Protected under right-to-repair principles

**This is NOT:**
- Piracy (you own the hardware)
- Copyright infringement (modifying your own device)
- Illegal (in most countries)
- Against Peloton's TOS for personal use

---

**Last Updated:** August 11, 2026  
**Status:** Complete Reference Guide  
**For:** Peloton Bike/Tread/Guide owners seeking device freedom

---

## Next Steps

1. **Now:** Read this guide and understand the restrictions
2. **Use PeloGo:** Click the "Disable Restrictions" button in PeloGo's Advanced Options
3. **Verify:** Check that systempluginui is disabled
4. **Enjoy:** Full device freedom while keeping Peloton functionality

Enjoy your device! 🚀
