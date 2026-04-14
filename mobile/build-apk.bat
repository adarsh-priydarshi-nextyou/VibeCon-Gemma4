@echo off
REM Voice Analysis App - APK Build Script (Windows)
REM This script automates the APK building process

echo.
echo Voice Analysis App - APK Builder
echo ====================================
echo.

REM Check if we're in the mobile directory
if not exist "package.json" (
    echo Error: Please run this script from the mobile directory
    exit /b 1
)

REM Step 1: Check Node.js
echo Step 1: Checking Node.js...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js not found. Please install Node.js 18+
    exit /b 1
)
node -v
echo.

REM Step 2: Check Java
echo Step 2: Checking Java...
where java >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Java not found. Please install JDK 17
    exit /b 1
)
java -version
echo.

REM Step 3: Check Android SDK
echo Step 3: Checking Android SDK...
if "%ANDROID_HOME%"=="" (
    echo Error: ANDROID_HOME not set
    echo Please set ANDROID_HOME environment variable
    exit /b 1
)
echo ANDROID_HOME: %ANDROID_HOME%
echo.

REM Step 4: Install dependencies
echo Step 4: Installing dependencies...
if not exist "node_modules" (
    echo Installing npm packages...
    call npm install
) else (
    echo Dependencies already installed
)
echo.

REM Step 5: Clean previous builds
echo Step 5: Cleaning previous builds...
cd android
call gradlew clean >nul 2>&1
cd ..
echo Clean complete
echo.

REM Step 6: Build APK
echo Step 6: Building APK...
echo This may take 3-10 minutes on first build...
echo.

set BUILD_TYPE=%1
if "%BUILD_TYPE%"=="" set BUILD_TYPE=debug

cd android
if "%BUILD_TYPE%"=="release" (
    echo Building RELEASE APK...
    call gradlew assembleRelease
    set APK_PATH=app\build\outputs\apk\release\app-release.apk
) else (
    echo Building DEBUG APK...
    call gradlew assembleDebug
    set APK_PATH=app\build\outputs\apk\debug\app-debug.apk
)
cd ..

echo.
echo Build complete!
echo.

REM Step 7: Show APK location
echo Step 7: APK Location
echo ========================================
echo APK: android\%APK_PATH%
echo.

REM Step 8: Check for connected devices
echo Step 8: Checking for connected devices...
where adb >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    adb devices | find "device" >nul
    if %ERRORLEVEL% EQU 0 (
        echo Found connected device(s)
        echo.
        set /p INSTALL_NOW="Would you like to install the APK now? (y/n): "
        if /i "%INSTALL_NOW%"=="y" (
            echo Installing APK...
            adb install -r "android\%APK_PATH%"
            echo APK installed successfully!
        )
    ) else (
        echo No devices connected
        echo.
        echo To install manually:
        echo 1. Connect your phone via USB
        echo 2. Enable USB debugging
        echo 3. Run: adb install android\%APK_PATH%
    )
) else (
    echo ADB not found
    echo Copy android\%APK_PATH% to your phone and install
)

echo.
echo ========================================
echo Build process complete!
echo ========================================
echo.
echo Next steps:
echo 1. Install the APK on your phone
echo 2. Grant microphone permission
echo 3. Test voice recording
echo 4. Verify offline functionality
echo.
echo For detailed instructions, see DEPLOYMENT_GUIDE.md
echo.

pause
