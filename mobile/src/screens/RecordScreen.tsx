/**
 * Record Screen - Voice Recording and Analysis
 */

import React, {useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import {check, request, PERMISSIONS, RESULTS} from 'react-native-permissions';
import AudioRecorderPlayer from 'react-native-audio-recorder-player';
import LinearGradient from 'react-native-linear-gradient';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import {processAudioLocally} from '../services/MLService';
import {storeVoiceAnalysis, getStatistics} from '../services/DatabaseService';
import apiService from '../services/APIService';

const audioRecorderPlayer = new AudioRecorderPlayer();

const RecordScreen = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [stressScore, setStressScore] = useState<number | null>(null);
  const [backendConnected, setBackendConnected] = useState(false);
  const [stats, setStats] = useState({
    totalRecordings: 0,
    avgStress: 0,
    trend: 'stable',
  });

  React.useEffect(() => {
    loadStats();
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      const isConnected = await apiService.checkHealth();
      setBackendConnected(isConnected);
      console.log('Backend connection:', isConnected ? 'Connected' : 'Offline');
    } catch (error) {
      setBackendConnected(false);
    }
  };

  const loadStats = async () => {
    const statistics = await getStatistics();
    setStats(statistics);
  };

  const checkMicrophonePermission = async (): Promise<boolean> => {
    try {
      const result = await check(PERMISSIONS.ANDROID.RECORD_AUDIO);

      if (result === RESULTS.GRANTED) {
        return true;
      }

      const requestResult = await request(PERMISSIONS.ANDROID.RECORD_AUDIO);
      return requestResult === RESULTS.GRANTED;
    } catch (error) {
      console.error('Permission error:', error);
      return false;
    }
  };

  const startRecording = async () => {
    try {
      const hasPermission = await checkMicrophonePermission();
      if (!hasPermission) {
        Alert.alert(
          'Permission Required',
          'Microphone permission is required to record audio',
        );
        return;
      }

      const path = `${audioRecorderPlayer.dirs.CacheDir}/recording_${Date.now()}.wav`;
      
      await audioRecorderPlayer.startRecorder(path);
      audioRecorderPlayer.addRecordBackListener(e => {
        setRecordingTime(Math.floor(e.currentPosition / 1000));
      });

      setIsRecording(true);
      setRecordingTime(0);
    } catch (error) {
      console.error('Failed to start recording:', error);
      Alert.alert('Error', 'Failed to start recording');
    }
  };

  const stopRecording = async () => {
    try {
      const result = await audioRecorderPlayer.stopRecorder();
      audioRecorderPlayer.removeRecordBackListener();
      setIsRecording(false);

      // Process audio
      await processAudio(result);
    } catch (error) {
      console.error('Failed to stop recording:', error);
      Alert.alert('Error', 'Failed to stop recording');
    }
  };

  const processAudio = async (audioPath: string) => {
    try {
      setIsProcessing(true);

      // Process audio locally
      const result = await processAudioLocally(audioPath);

      // Store in database
      await storeVoiceAnalysis({
        timestamp: new Date().toISOString(),
        stressScore: result.stressScore,
        features: result.features,
        linguisticSummary: result.linguisticSummary,
        audioDuration: recordingTime,
      });

      // Update UI
      setStressScore(result.stressScore);
      await loadStats();

      Alert.alert(
        'Analysis Complete',
        `Your stress level is ${(result.stressScore * 100).toFixed(0)}%`,
      );
    } catch (error) {
      console.error('Failed to process audio:', error);
      Alert.alert('Error', 'Failed to process audio');
    } finally {
      setIsProcessing(false);
    }
  };

  const getStressLevel = (score: number) => {
    if (score < 0.3) {
      return {label: 'Low', color: '#48bb78', emoji: '😌'};
    }
    if (score < 0.6) {
      return {label: 'Moderate', color: '#ed8936', emoji: '😐'};
    }
    return {label: 'High', color: '#f56565', emoji: '😰'};
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const level = stressScore !== null ? getStressLevel(stressScore) : null;

  return (
    <ScrollView style={styles.container}>
      {/* Backend Status Banner */}
      <View
        style={[
          styles.statusBanner,
          {backgroundColor: backendConnected ? '#48bb78' : '#ed8936'},
        ]}>
        <Icon
          name={backendConnected ? 'cloud-check' : 'cloud-off-outline'}
          size={16}
          color="#ffffff"
        />
        <Text style={styles.statusText}>
          {backendConnected
            ? '🟢 Connected to Backend - Using Real ML Models'
            : '🟡 Offline Mode - Using Local Processing'}
        </Text>
      </View>

      {/* Stats Cards */}
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>{stats.totalRecordings}</Text>
          <Text style={styles.statLabel}>Recordings</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>
            {Math.round(stats.avgStress * 100)}%
          </Text>
          <Text style={styles.statLabel}>Avg Stress</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statValue}>
            {stats.trend === 'increasing'
              ? '📈'
              : stats.trend === 'decreasing'
              ? '📉'
              : '➡️'}
          </Text>
          <Text style={styles.statLabel}>Trend</Text>
        </View>
      </View>

      {/* Recording Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Voice Recording</Text>
        <Text style={styles.cardSubtitle}>
          Record your voice to analyze stress levels
        </Text>

        <View style={styles.recordingContainer}>
          {!isRecording && !isProcessing && (
            <TouchableOpacity
              style={styles.recordButton}
              onPress={startRecording}>
              <LinearGradient
                colors={['#667eea', '#764ba2']}
                style={styles.recordButtonGradient}>
                <Icon name="microphone" size={40} color="#ffffff" />
                <Text style={styles.recordButtonText}>Start Recording</Text>
              </LinearGradient>
            </TouchableOpacity>
          )}

          {isRecording && (
            <View style={styles.recordingActive}>
              <View style={styles.recordingIndicator}>
                <View style={styles.pulse} />
                <Text style={styles.recordingText}>Recording...</Text>
              </View>
              <Text style={styles.recordingTime}>{formatTime(recordingTime)}</Text>
              <TouchableOpacity
                style={styles.stopButton}
                onPress={stopRecording}>
                <Icon name="stop" size={30} color="#ffffff" />
                <Text style={styles.stopButtonText}>Stop Recording</Text>
              </TouchableOpacity>
            </View>
          )}

          {isProcessing && (
            <View style={styles.processingContainer}>
              <ActivityIndicator size="large" color="#667eea" />
              <Text style={styles.processingText}>Processing audio...</Text>
            </View>
          )}
        </View>

        <View style={styles.infoBox}>
          <Text style={styles.infoText}>💡 Speak naturally for 10-30 seconds</Text>
          <Text style={styles.infoText}>
            {backendConnected
              ? '🔬 Using real ML models (SenseVoice, wav2vec2, Gemma4)'
              : '📱 Processing locally on device'}
          </Text>
        </View>
      </View>

      {/* Stress Result */}
      {level && (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Your Stress Level</Text>
          <View style={styles.stressResult}>
            <Text style={styles.stressEmoji}>{level.emoji}</Text>
            <View style={styles.stressInfo}>
              <Text style={styles.stressLabel}>{level.label} Stress</Text>
              <Text style={styles.stressPercentage}>
                {Math.round(stressScore! * 100)}%
              </Text>
            </View>
          </View>
          <View style={styles.stressBarContainer}>
            <View
              style={[
                styles.stressBar,
                {
                  width: `${stressScore! * 100}%`,
                  backgroundColor: level.color,
                },
              ]}
            />
          </View>
          <View style={styles.stressScale}>
            <Text style={styles.scaleText}>Low</Text>
            <Text style={styles.scaleText}>Moderate</Text>
            <Text style={styles.scaleText}>High</Text>
          </View>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f7fafc',
  },
  statusBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    gap: 8,
  },
  statusText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '700',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#ffffff',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
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
    textTransform: 'uppercase',
  },
  card: {
    backgroundColor: '#ffffff',
    margin: 16,
    marginTop: 0,
    padding: 24,
    borderRadius: 16,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 8,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#2d3748',
    marginBottom: 8,
  },
  cardSubtitle: {
    fontSize: 14,
    color: '#718096',
    marginBottom: 24,
  },
  recordingContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  recordButton: {
    width: 200,
    height: 200,
    borderRadius: 100,
    overflow: 'hidden',
  },
  recordButtonGradient: {
    width: '100%',
    height: '100%',
    alignItems: 'center',
    justifyContent: 'center',
  },
  recordButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
    marginTop: 8,
  },
  recordingActive: {
    alignItems: 'center',
    gap: 20,
  },
  recordingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  pulse: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#f56565',
  },
  recordingText: {
    fontSize: 18,
    fontWeight: '700',
    color: '#f56565',
  },
  recordingTime: {
    fontSize: 48,
    fontWeight: '800',
    color: '#2d3748',
    fontFamily: 'monospace',
  },
  stopButton: {
    backgroundColor: '#f56565',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  stopButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },
  processingContainer: {
    alignItems: 'center',
    gap: 16,
    paddingVertical: 40,
  },
  processingText: {
    fontSize: 16,
    color: '#718096',
    fontWeight: '600',
  },
  infoBox: {
    backgroundColor: '#f7fafc',
    padding: 16,
    borderRadius: 12,
    gap: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#4a5568',
    fontWeight: '500',
  },
  stressResult: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
    marginBottom: 20,
  },
  stressEmoji: {
    fontSize: 56,
  },
  stressInfo: {
    flex: 1,
  },
  stressLabel: {
    fontSize: 18,
    fontWeight: '700',
    color: '#2d3748',
    marginBottom: 4,
  },
  stressPercentage: {
    fontSize: 32,
    fontWeight: '800',
    color: '#4a5568',
  },
  stressBarContainer: {
    height: 40,
    backgroundColor: '#e2e8f0',
    borderRadius: 20,
    overflow: 'hidden',
    marginBottom: 12,
  },
  stressBar: {
    height: '100%',
    borderRadius: 20,
  },
  stressScale: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  scaleText: {
    fontSize: 12,
    color: '#718096',
    fontWeight: '600',
  },
});

export default RecordScreen;
