# 🚀 Quick Start Guide

## Build APK in 3 Steps

### Step 1: Install Dependencies
```bash
cd mobile
npm install
```

### Step 2: Build APK
```bash
# macOS/Linux
./build-apk.sh

# Windows
build-apk.bat
```

### Step 3: Install on Phone
```bash
# Connect phone via USB with USB debugging enabled
adb install android/app/build/outputs/apk/debug/app-debug.apk
```

---

## ⚡ Super Quick Commands

### Build Debug APK
```bash
cd mobile/android
./gradlew assembleDebug
```
**APK**: `android/app/build/outputs/apk/debug/app-debug.apk`

### Build Release APK
```bash
cd mobile/android
./gradlew assembleRelease
```
**APK**: `android/app/build/outputs/apk/release/app-release.apk`

### Install APK
```bash
adb install path/to/app.apk
```

### Uninstall App
```bash
adb uninstall com.voiceanalysisapp
```

---

## 📋 Prerequisites Checklist

- [ ] Node.js 18+ installed
- [ ] JDK 17 installed
- [ ] Android Studio installed
- [ ] ANDROID_HOME environment variable set
- [ ] USB debugging enabled on phone (for installation)

---

## 🔧 Environment Setup

### macOS/Linux
```bash
# Add to ~/.bashrc or ~/.zshrc
export ANDROID_HOME=$HOME/Library/Android/sdk  # macOS
# OR
export ANDROID_HOME=$HOME/Android/Sdk  # Linux

export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/platform-tools

# Reload
source ~/.bashrc  # or ~/.zshrc
```

### Windows
```cmd
# Set in System Environment Variables
ANDROID_HOME=C:\Users\YourName\AppData\Local\Android\Sdk

# Add to PATH
%ANDROID_HOME%\platform-tools
%ANDROID_HOME%\emulator
```

---

## 🎯 Testing Checklist

After installing APK:

### Basic Functionality
- [ ] App launches successfully
- [ ] Microphone permission granted
- [ ] Can record voice (5-10 seconds)
- [ ] Processing completes (~2 seconds)
- [ ] Stress score displays (0-100%)
- [ ] Statistics update

### Insights (Need 3+ recordings)
- [ ] Pattern detected (increasing/decreasing/stable)
- [ ] Contributing factors shown
- [ ] Observations displayed
- [ ] Trend indicator works

### Interventions
- [ ] 3 recommendations shown
- [ ] Recommendations match stress level
- [ ] Like/dislike buttons work

### Offline Mode
- [ ] Enable airplane mode
- [ ] Record voice
- [ ] Processing works
- [ ] Insights generate
- [ ] Everything works offline ✅

---

## 🐛 Common Issues

### Build Fails
```bash
# Clean and rebuild
cd android
./gradlew clean
./gradlew assembleDebug
```

### Device Not Found
```bash
# Check connection
adb devices

# Restart adb
adb kill-server
adb start-server
```

### Permission Denied
```bash
# Make script executable
chmod +x build-apk.sh
```

### App Crashes
```bash
# View logs
adb logcat | grep VoiceAnalysis
```

---

## 📱 Installation Methods

### Method 1: USB (Recommended)
1. Enable USB debugging on phone
2. Connect via USB
3. Run: `adb install path/to/app.apk`

### Method 2: Direct Download
1. Copy APK to phone (email/drive/USB)
2. Open APK file on phone
3. Allow "Install from Unknown Sources"
4. Tap "Install"

---

## 🎨 App Features

### Record Screen
- Voice recording with timer
- Real-time stress analysis
- Visual stress meter
- Statistics cards

### Insights Screen
- Pattern visualization
- Contributing factors
- Observations
- Trend analysis

### Interventions Screen
- Top 3 recommendations
- Audio playback (placeholder)
- Like/dislike feedback
- Usage tracking

### Settings Screen
- User preferences
- Data management
- Model information
- Privacy settings

---

## 📊 Expected Performance

- **App Size**: ~30MB
- **Startup**: ~2 seconds
- **Processing**: 1-3 seconds per recording
- **Memory**: ~100-150MB
- **Battery**: Low impact

---

## 🔐 Privacy Features

- ✅ All data stored locally
- ✅ No internet required
- ✅ No data upload
- ✅ No tracking
- ✅ Complete offline operation

---

## 📞 Need Help?

See **DEPLOYMENT_GUIDE.md** for detailed instructions.

---

**Happy Building! 🎙️✨**
