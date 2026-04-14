/**
 * Settings Screen - App settings and preferences
 */

import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Switch,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import AsyncStorage from '@react-native-async-storage/async-storage';

import {
  getUserId,
  clearAllData,
  getStatistics,
} from '../services/DatabaseService';

const SettingsScreen = () => {
  const [userId, setUserId] = useState('');
  const [stats, setStats] = useState({totalRecordings: 0, avgStress: 0});
  const [notifications, setNotifications] = useState(true);
  const [autoBackup, setAutoBackup] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    const id = await getUserId();
    setUserId(id);

    const statistics = await getStatistics();
    setStats(statistics);

    const notifPref = await AsyncStorage.getItem('notifications_enabled');
    setNotifications(notifPref !== 'false');

    const backupPref = await AsyncStorage.getItem('auto_backup_enabled');
    setAutoBackup(backupPref === 'true');
  };

  const handleClearData = () => {
    Alert.alert(
      'Clear All Data',
      'This will delete all recordings, insights, and settings. This action cannot be undone.',
      [
        {text: 'Cancel', style: 'cancel'},
        {
          text: 'Clear',
          style: 'destructive',
          onPress: async () => {
            await clearAllData();
            await loadSettings();
            Alert.alert('Success', 'All data has been cleared');
          },
        },
      ],
    );
  };

  const handleToggleNotifications = async (value: boolean) => {
    setNotifications(value);
    await AsyncStorage.setItem('notifications_enabled', value.toString());
  };

  const handleToggleAutoBackup = async (value: boolean) => {
    setAutoBackup(value);
    await AsyncStorage.setItem('auto_backup_enabled', value.toString());
  };

  const SettingItem = ({
    icon,
    title,
    subtitle,
    onPress,
    rightElement,
  }: any) => (
    <TouchableOpacity
      style={styles.settingItem}
      onPress={onPress}
      disabled={!onPress}>
      <View style={styles.settingLeft}>
        <Icon name={icon} size={24} color="#667eea" />
        <View style={styles.settingText}>
          <Text style={styles.settingTitle}>{title}</Text>
          {subtitle && <Text style={styles.settingSubtitle}>{subtitle}</Text>}
        </View>
      </View>
      {rightElement || (
        onPress && <Icon name="chevron-right" size={24} color="#cbd5e0" />
      )}
    </TouchableOpacity>
  );

  return (
    <ScrollView style={styles.container}>
      {/* User Info */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>User Information</Text>
        <View style={styles.card}>
          <View style={styles.userInfo}>
            <Icon name="account-circle" size={60} color="#667eea" />
            <View style={styles.userDetails}>
              <Text style={styles.userName}>Mobile User</Text>
              <Text style={styles.userId}>{userId}</Text>
            </View>
          </View>
          <View style={styles.statsRow}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{stats.totalRecordings}</Text>
              <Text style={styles.statLabel}>Recordings</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>
                {Math.round(stats.avgStress * 100)}%
              </Text>
              <Text style={styles.statLabel}>Avg Stress</Text>
            </View>
          </View>
        </View>
      </View>

      {/* Preferences */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Preferences</Text>
        <View style={styles.card}>
          <SettingItem
            icon="bell"
            title="Notifications"
            subtitle="Receive reminders and updates"
            rightElement={
              <Switch
                value={notifications}
                onValueChange={handleToggleNotifications}
                trackColor={{false: '#cbd5e0', true: '#667eea'}}
                thumbColor="#ffffff"
              />
            }
          />
          <View style={styles.divider} />
          <SettingItem
            icon="cloud-upload"
            title="Auto Backup"
            subtitle="Automatically backup data (coming soon)"
            rightElement={
              <Switch
                value={autoBackup}
                onValueChange={handleToggleAutoBackup}
                trackColor={{false: '#cbd5e0', true: '#667eea'}}
                thumbColor="#ffffff"
                disabled
              />
            }
          />
        </View>
      </View>

      {/* Privacy */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Privacy & Security</Text>
        <View style={styles.card}>
          <SettingItem
            icon="shield-check"
            title="Privacy Policy"
            subtitle="How we protect your data"
            onPress={() => Alert.alert('Privacy', 'All data is stored locally on your device. Nothing is sent to external servers.')}
          />
          <View style={styles.divider} />
          <SettingItem
            icon="lock"
            title="Data Encryption"
            subtitle="Your data is encrypted"
            rightElement={
              <Icon name="check-circle" size={24} color="#48bb78" />
            }
          />
        </View>
      </View>

      {/* ML Models */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>ML Models</Text>
        <View style={styles.card}>
          <SettingItem
            icon="brain"
            title="SenseVoice"
            subtitle="Audio feature extraction"
            rightElement={
              <Icon name="check-circle" size={24} color="#48bb78" />
            }
          />
          <View style={styles.divider} />
          <SettingItem
            icon="waveform"
            title="wav2vec2"
            subtitle="Contextual embeddings"
            rightElement={
              <Icon name="check-circle" size={24} color="#48bb78" />
            }
          />
          <View style={styles.divider} />
          <SettingItem
            icon="robot"
            title="Gemma"
            subtitle="Insights generation"
            rightElement={
              <Icon name="check-circle" size={24} color="#48bb78" />
            }
          />
        </View>
      </View>

      {/* Data Management */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Data Management</Text>
        <View style={styles.card}>
          <SettingItem
            icon="download"
            title="Export Data"
            subtitle="Export your data (coming soon)"
            onPress={() => Alert.alert('Coming Soon', 'Data export feature will be available in the next update')}
          />
          <View style={styles.divider} />
          <TouchableOpacity
            style={styles.settingItem}
            onPress={handleClearData}>
            <View style={styles.settingLeft}>
              <Icon name="delete" size={24} color="#f56565" />
              <View style={styles.settingText}>
                <Text style={[styles.settingTitle, {color: '#f56565'}]}>
                  Clear All Data
                </Text>
                <Text style={styles.settingSubtitle}>
                  Delete all recordings and settings
                </Text>
              </View>
            </View>
            <Icon name="chevron-right" size={24} color="#cbd5e0" />
          </TouchableOpacity>
        </View>
      </View>

      {/* About */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        <View style={styles.card}>
          <SettingItem
            icon="information"
            title="Version"
            subtitle="1.0.0"
          />
          <View style={styles.divider} />
          <SettingItem
            icon="code-tags"
            title="Open Source"
            subtitle="MIT License"
          />
        </View>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>
          Voice Analysis & Intervention System
        </Text>
        <Text style={styles.footerSubtext}>
          Privacy-first AI-powered wellness platform
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f7fafc',
  },
  section: {
    marginTop: 24,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#4a5568',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginLeft: 16,
    marginBottom: 8,
  },
  card: {
    backgroundColor: '#ffffff',
    marginHorizontal: 16,
    borderRadius: 12,
    overflow: 'hidden',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 1},
    shadowOpacity: 0.05,
    shadowRadius: 4,
  },
  userInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
    padding: 20,
  },
  userDetails: {
    flex: 1,
  },
  userName: {
    fontSize: 20,
    fontWeight: '700',
    color: '#2d3748',
    marginBottom: 4,
  },
  userId: {
    fontSize: 12,
    color: '#718096',
    fontFamily: 'monospace',
  },
  statsRow: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
  },
  statItem: {
    flex: 1,
    padding: 16,
    alignItems: 'center',
    borderRightWidth: 1,
    borderRightColor: '#e2e8f0',
  },
  statValue: {
    fontSize: 24,
    fontWeight: '800',
    color: '#667eea',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#718096',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    flex: 1,
  },
  settingText: {
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2d3748',
    marginBottom: 2,
  },
  settingSubtitle: {
    fontSize: 13,
    color: '#718096',
  },
  divider: {
    height: 1,
    backgroundColor: '#e2e8f0',
    marginLeft: 52,
  },
  footer: {
    padding: 32,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4a5568',
    marginBottom: 4,
  },
  footerSubtext: {
    fontSize: 12,
    color: '#718096',
  },
});

export default SettingsScreen;
