/**
 * API Configuration
 * Update the API_BASE_URL to match your backend server
 */

// For Android Emulator: Use 10.0.2.2 (maps to host machine's localhost)
// For iOS Simulator: Use localhost or 127.0.0.1
// For Real Device: Use your computer's local IP address (e.g., 192.168.1.100)

export const API_CONFIG = {
  // Android Emulator
  ANDROID_EMULATOR: 'http://10.0.2.2:8000',
  
  // iOS Simulator
  IOS_SIMULATOR: 'http://localhost:8000',
  
  // Real Device (Update with your computer's IP)
  REAL_DEVICE: 'http://192.168.1.100:8000',
  
  // Production (if deployed)
  PRODUCTION: 'https://your-backend-url.com',
};

// Auto-detect platform and environment
import {Platform} from 'react-native';

export const getAPIBaseURL = (): string => {
  // Check if running on emulator/simulator or real device
  // For now, default to emulator/simulator
  
  if (Platform.OS === 'android') {
    // Android emulator
    return API_CONFIG.ANDROID_EMULATOR;
  } else if (Platform.OS === 'ios') {
    // iOS simulator
    return API_CONFIG.IOS_SIMULATOR;
  }
  
  // Fallback
  return API_CONFIG.ANDROID_EMULATOR;
};

// Instructions for finding your local IP:
// 
// macOS/Linux:
//   Run: ifconfig | grep "inet " | grep -v 127.0.0.1
//   Look for: inet 192.168.x.x
//
// Windows:
//   Run: ipconfig
//   Look for: IPv4 Address: 192.168.x.x
//
// Then update API_CONFIG.REAL_DEVICE with your IP address
