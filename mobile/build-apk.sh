#!/bin/bash

# Voice Analysis App - APK Build Script
# This script automates the APK building process

set -e  # Exit on error

echo "🎙️ Voice Analysis App - APK Builder"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the mobile directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: Please run this script from the mobile directory${NC}"
    exit 1
fi

# Step 1: Check Node.js
echo -e "${BLUE}📦 Step 1: Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
NODE_VERSION=$(node -v)
echo -e "${GREEN}✅ Node.js $NODE_VERSION found${NC}"
echo ""

# Step 2: Check Java
echo -e "${BLUE}☕ Step 2: Checking Java...${NC}"
if ! command -v java &> /dev/null; then
    echo -e "${RED}❌ Java not found. Please install JDK 17${NC}"
    exit 1
fi
JAVA_VERSION=$(java -version 2>&1 | head -n 1)
echo -e "${GREEN}✅ $JAVA_VERSION found${NC}"
echo ""

# Step 3: Check Android SDK
echo -e "${BLUE}🤖 Step 3: Checking Android SDK...${NC}"
if [ -z "$ANDROID_HOME" ]; then
    echo -e "${YELLOW}⚠️  ANDROID_HOME not set${NC}"
    echo "Please set ANDROID_HOME environment variable"
    echo "Example: export ANDROID_HOME=\$HOME/Library/Android/sdk"
    exit 1
fi
echo -e "${GREEN}✅ ANDROID_HOME: $ANDROID_HOME${NC}"
echo ""

# Step 4: Install dependencies
echo -e "${BLUE}📥 Step 4: Installing dependencies...${NC}"
if [ ! -d "node_modules" ]; then
    echo "Installing npm packages..."
    npm install
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Dependencies already installed${NC}"
fi
echo ""

# Step 5: Clean previous builds
echo -e "${BLUE}🧹 Step 5: Cleaning previous builds...${NC}"
cd android
./gradlew clean > /dev/null 2>&1 || true
echo -e "${GREEN}✅ Clean complete${NC}"
echo ""

# Step 6: Build APK
echo -e "${BLUE}🔨 Step 6: Building APK...${NC}"
echo "This may take 3-10 minutes on first build..."
echo ""

BUILD_TYPE=${1:-debug}  # Default to debug, can pass 'release' as argument

if [ "$BUILD_TYPE" = "release" ]; then
    echo "Building RELEASE APK..."
    ./gradlew assembleRelease
    APK_PATH="app/build/outputs/apk/release/app-release.apk"
else
    echo "Building DEBUG APK..."
    ./gradlew assembleDebug
    APK_PATH="app/build/outputs/apk/debug/app-debug.apk"
fi

cd ..

echo ""
echo -e "${GREEN}✅ Build complete!${NC}"
echo ""

# Step 7: Show APK location
echo -e "${BLUE}📱 Step 7: APK Location${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "APK: ${GREEN}android/$APK_PATH${NC}"
echo ""

# Step 8: Check if device is connected
echo -e "${BLUE}🔌 Step 8: Checking for connected devices...${NC}"
if command -v adb &> /dev/null; then
    DEVICES=$(adb devices | grep -v "List" | grep "device" | wc -l)
    if [ "$DEVICES" -gt 0 ]; then
        echo -e "${GREEN}✅ Found $DEVICES connected device(s)${NC}"
        echo ""
        echo -e "${YELLOW}Would you like to install the APK now? (y/n)${NC}"
        read -r INSTALL_NOW
        if [ "$INSTALL_NOW" = "y" ] || [ "$INSTALL_NOW" = "Y" ]; then
            echo "Installing APK..."
            adb install -r "android/$APK_PATH"
            echo -e "${GREEN}✅ APK installed successfully!${NC}"
            echo ""
            echo "You can now open the app on your device"
        fi
    else
        echo -e "${YELLOW}⚠️  No devices connected${NC}"
        echo ""
        echo "To install manually:"
        echo "1. Connect your phone via USB"
        echo "2. Enable USB debugging"
        echo "3. Run: adb install android/$APK_PATH"
        echo ""
        echo "Or copy the APK to your phone and install directly"
    fi
else
    echo -e "${YELLOW}⚠️  ADB not found${NC}"
    echo "Copy android/$APK_PATH to your phone and install"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 Build process complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Install the APK on your phone"
echo "2. Grant microphone permission"
echo "3. Test voice recording"
echo "4. Verify offline functionality"
echo ""
echo "For detailed instructions, see DEPLOYMENT_GUIDE.md"
echo ""
