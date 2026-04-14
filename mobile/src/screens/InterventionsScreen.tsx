/**
 * Interventions Screen - Recommendations and playback
 */

import React, {useState, useCallback} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Alert,
} from 'react-native';
import {useFocusEffect} from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import {getRecentVoiceScores, storeTelemetry} from '../services/DatabaseService';
import {getRecommendations} from '../services/MLService';

const InterventionsScreen = () => {
  const [interventions, setInterventions] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);
  const [playingId, setPlayingId] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      loadInterventions();
    }, []),
  );

  const loadInterventions = async () => {
    try {
      const voiceScores = await getRecentVoiceScores(3);
      
      if (voiceScores.length === 0) {
        setInterventions([]);
        return;
      }

      const avgStress =
        voiceScores.reduce((a, b) => a + b, 0) / voiceScores.length;
      
      // Determine pattern
      let pattern = 'stable';
      if (voiceScores.length >= 3) {
        const trend = voiceScores[voiceScores.length - 1] - voiceScores[0];
        if (trend > 0.1) pattern = 'increasing';
        else if (trend < -0.1) pattern = 'decreasing';
      }

      const recommendations = await getRecommendations(pattern, avgStress);
      setInterventions(recommendations);
    } catch (error) {
      console.error('Failed to load interventions:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadInterventions();
    setRefreshing(false);
  };

  const handlePlay = async (intervention: any) => {
    setPlayingId(intervention.id);
    
    // Simulate playback
    setTimeout(async () => {
      await storeTelemetry({
        audioId: intervention.id,
        timestamp: new Date().toISOString(),
        playDuration: intervention.duration,
        totalDuration: intervention.duration,
        completed: true,
        likeStatus: null,
      });
      
      setPlayingId(null);
      Alert.alert('Playback Complete', 'How did you find this intervention?');
    }, 3000); // Simulate 3 seconds
  };

  const handleFeedback = async (intervention: any, liked: boolean) => {
    await storeTelemetry({
      audioId: intervention.id,
      timestamp: new Date().toISOString(),
      playDuration: intervention.duration,
      totalDuration: intervention.duration,
      completed: true,
      likeStatus: liked,
    });

    Alert.alert(
      'Thank You!',
      'Your feedback helps us improve recommendations',
    );
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'breathing':
        return 'lungs';
      case 'meditation':
        return 'meditation';
      case 'music':
        return 'music';
      default:
        return 'headphones';
    }
  };

  if (interventions.length === 0) {
    return (
      <ScrollView
        style={styles.container}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }>
        <View style={styles.emptyState}>
          <Icon name="headphones-off" size={80} color="#cbd5e0" />
          <Text style={styles.emptyTitle}>No Recommendations Yet</Text>
          <Text style={styles.emptyText}>
            Record voice samples to get personalized interventions
          </Text>
          <TouchableOpacity style={styles.refreshButton} onPress={onRefresh}>
            <Icon name="refresh" size={20} color="#ffffff" />
            <Text style={styles.refreshButtonText}>Refresh</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Recommended Interventions</Text>
        <TouchableOpacity onPress={onRefresh}>
          <Icon name="refresh" size={24} color="#667eea" />
        </TouchableOpacity>
      </View>

      {interventions.map((intervention, index) => (
        <View key={intervention.id} style={styles.interventionCard}>
          <View style={styles.rankBadge}>
            <Text style={styles.rankText}>#{index + 1}</Text>
          </View>

          <View style={styles.interventionHeader}>
            <Icon
              name={getCategoryIcon(intervention.category)}
              size={32}
              color="#667eea"
            />
            <View style={styles.interventionHeaderText}>
              <Text style={styles.interventionTitle}>{intervention.title}</Text>
              <View style={styles.interventionMeta}>
                <View style={styles.badge}>
                  <Text style={styles.badgeText}>{intervention.category}</Text>
                </View>
                <Text style={styles.duration}>
                  ⏱️ {Math.floor(intervention.duration / 60)}m
                </Text>
              </View>
            </View>
          </View>

          <Text style={styles.interventionDescription}>
            {intervention.description}
          </Text>

          <View style={styles.reasonBox}>
            <Icon name="target" size={20} color="#48bb78" />
            <Text style={styles.reasonText}>{intervention.reasoning}</Text>
            <Text style={styles.relevanceScore}>
              {Math.round(intervention.relevanceScore * 100)}%
            </Text>
          </View>

          <View style={styles.interventionActions}>
            {playingId === intervention.id ? (
              <View style={styles.playingIndicator}>
                <View style={styles.pulse} />
                <Text style={styles.playingText}>Playing...</Text>
              </View>
            ) : (
              <>
                <TouchableOpacity
                  style={styles.playButton}
                  onPress={() => handlePlay(intervention)}>
                  <Icon name="play" size={20} color="#ffffff" />
                  <Text style={styles.playButtonText}>Play</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={styles.feedbackButton}
                  onPress={() => handleFeedback(intervention, true)}>
                  <Icon name="thumb-up" size={20} color="#48bb78" />
                </TouchableOpacity>
                <TouchableOpacity
                  style={styles.feedbackButton}
                  onPress={() => handleFeedback(intervention, false)}>
                  <Icon name="thumb-down" size={20} color="#f56565" />
                </TouchableOpacity>
              </>
            )}
          </View>
        </View>
      ))}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f7fafc',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#2d3748',
  },
  interventionCard: {
    backgroundColor: '#ffffff',
    margin: 16,
    marginTop: 0,
    padding: 20,
    borderRadius: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#48bb78',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 8,
    position: 'relative',
  },
  rankBadge: {
    position: 'absolute',
    top: 16,
    right: 16,
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#48bb78',
    alignItems: 'center',
    justifyContent: 'center',
  },
  rankText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '800',
  },
  interventionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 12,
    paddingRight: 40,
  },
  interventionHeaderText: {
    flex: 1,
  },
  interventionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#2d3748',
    marginBottom: 6,
  },
  interventionMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  badge: {
    backgroundColor: '#edf2f7',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#4a5568',
    textTransform: 'uppercase',
  },
  duration: {
    fontSize: 13,
    color: '#718096',
    fontWeight: '600',
  },
  interventionDescription: {
    fontSize: 15,
    color: '#4a5568',
    lineHeight: 22,
    marginBottom: 16,
  },
  reasonBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    backgroundColor: '#f7fafc',
    padding: 12,
    borderRadius: 10,
    marginBottom: 16,
  },
  reasonText: {
    flex: 1,
    fontSize: 14,
    color: '#4a5568',
    fontWeight: '500',
  },
  relevanceScore: {
    fontSize: 13,
    fontWeight: '700',
    color: '#48bb78',
  },
  interventionActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  playButton: {
    flex: 1,
    backgroundColor: '#667eea',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 12,
    borderRadius: 10,
  },
  playButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },
  feedbackButton: {
    width: 48,
    height: 48,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f7fafc',
    borderRadius: 10,
  },
  playingIndicator: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 10,
    paddingVertical: 12,
  },
  pulse: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: '#4299e1',
  },
  playingText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#4299e1',
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
    minHeight: 400,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#2d3748',
    marginTop: 16,
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 16,
    color: '#718096',
    textAlign: 'center',
    marginBottom: 24,
  },
  refreshButton: {
    backgroundColor: '#667eea',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 12,
  },
  refreshButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
  },
});

export default InterventionsScreen;
