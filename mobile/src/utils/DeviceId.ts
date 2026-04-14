/**
 * Device ID Generator
 * Creates unique, persistent device ID based on device fingerprint
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import DeviceInfo from 'react-native-device-info';
import { Platform } from 'react-native';

const DEVICE_ID_KEY = 'device_id';

/**
 * Generate device ID from device fingerprint
 */
const generateDeviceId = async (): Promise<string> => {
  try {
    // Collect device information
    const uniqueId = await DeviceInfo.getUniqueId(); // Hardware ID
    const deviceId = DeviceInfo.getDeviceId(); // Model
    const systemVersion = DeviceInfo.getSystemVersion();
    const brand = await DeviceInfo.getBrand();
    
    // Create fingerprint
    const fingerprint = [
      uniqueId,
      deviceId,
      systemVersion,
      brand,
      Platform.OS
    ].join('|');
    
    // Create hash (simple hash function)
    let hash = 0;
    for (let i = 0; i < fingerprint.length; i++) {
      const char = fingerprint.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    
    // Create readable device ID
    const deviceIdStr = `device_${Math.abs(hash).toString(16).padStart(16, '0').substring(0, 16)}`;
    
    console.log('Generated device ID:', deviceIdStr);
    return deviceIdStr;
    
  } catch (error) {
    console.error('Error generating device ID:', error);
    // Fallback to random ID
    const randomId = `device_${Math.random().toString(16).substring(2, 18)}`;
    return randomId;
  }
};

/**
 * Get or create device ID (persistent across app sessions)
 */
export const getDeviceId = async (): Promise<string> => {
  try {
    // Check if device ID already exists
    let deviceId = await AsyncStorage.getItem(DEVICE_ID_KEY);
    
    if (!deviceId) {
      // Generate new device ID
      deviceId = await generateDeviceId();
      
      // Store for future use
      await AsyncStorage.setItem(DEVICE_ID_KEY, deviceId);
      console.log('Created and stored new device ID:', deviceId);
    } else {
      console.log('Using existing device ID:', deviceId);
    }
    
    return deviceId;
    
  } catch (error) {
    console.error('Error getting device ID:', error);
    // Return fallback ID
    return `device_${Date.now().toString(16)}`;
  }
};

/**
 * Get device info for API headers
 */
export const getDeviceInfo = async () => {
  try {
    const deviceId = await getDeviceId();
    const deviceName = await DeviceInfo.getDeviceName();
    const systemVersion = DeviceInfo.getSystemVersion();
    const appVersion = DeviceInfo.getVersion();
    
    return {
      deviceId,
      deviceName,
      platform: Platform.OS,
      systemVersion,
      appVersion,
    };
  } catch (error) {
    console.error('Error getting device info:', error);
    return {
      deviceId: await getDeviceId(),
      deviceName: 'Unknown',
      platform: Platform.OS,
      systemVersion: 'Unknown',
      appVersion: '1.0.0',
    };
  }
};

export default {
  getDeviceId,
  getDeviceInfo,
};
