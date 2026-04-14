/**
 * Insights Screen - Display stress patterns and insights
 */

import React, {useState, useCallback} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import {useFocusEffect} from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

import {
  getInsights,
  getRecentVoiceScores,
  getLatestBaseline,
  storeInsight,
} from '../services/DatabaseService';
import {generateInsights} from '../services/MLService';

const InsightsScreen = () => {
  const [insights, setInsights] = useState<any[]>([]);
  const [refreshing, setRefreshing] = useState(false);

  useFocusEffect(
    useCallback(() => {
      loadInsights();
    }, []),
  );

  const loadInsights = async () => {
    try {
      // Get stored insights
      const storedInsights = await getInsights();
      
      // If no insights or old insights, generate new ones
      if (storedInsights.length === 0) {
        await generateNewInsights();
      } else {
        setInsights(storedInsights);
      }
    } catch (error) {
      console.error('Failed to load insights:', error);
    }
  };

  const generateNewInsights = async () => {
    try {
      const voiceScores = await getRecentVoiceScores(3);
      const baseline = await getLatestBaseline();

      const insight = await generateInsights(
        voiceScores,
        baseline?.baselineStress || null,
      );

      await storeInsight({
        generationDate: new Date().toISOString(),
        pattern: insight.pattern,
        patternDescription: insight.patternDescription,
        contributingFactors: insight.contributingFactors,
        observations: insight.observations,
      });

      await loadInsights();
    } catch (error) {
      console.error('Failed to generate insights:', error);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await generateNewInsights();
    setRefreshing(false);
  };

  const getPatternIcon = (pattern: string) => {
    switch (pattern) {
      case 'increasing':
        return {icon: 'trending-up', color: '#f56565'};
      case 'decreasing':
        return {icon: 'trending-down', color: '#48bb78'};
      case 'stable':
        return {icon: 'trending-neutral', color: '#4299e1'};
      default:
        return {icon: 'chart-line', color: '#718096'};
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (insights.length === 0) {
    return (
      <ScrollView
        style={styles.container}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }>
        <View style={styles.emptyState}>
          <Icon name="chart-line-variant" size={80} color="#cbd5e0" />
          <Text style={styles.emptyTitle}>No Insights Yet</Text>
          <Text style={styles.emptyText}>
            Record at least 3 voice samples to generate insights
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
        <Text style={styles.headerTitle}>Your Insights</Text>
        <TouchableOpacity onPress={onRefresh}>
          <Icon name="refresh" size={24} color="#667eea" />
        </TouchableOpacity>
      </View>

      {insights.map((insight, index) => {
        const patternInfo = getPatternIcon(insight.pattern);
        return (
          <View key={insight.id || index} style={styles.insightCard}>
            <View style={styles.insightHeader}>
              <Icon
                name={patternInfo.icon}
                size={40}
                color={patternInfo.color}
              />
              <View style={styles.insightHeaderText}>
                <Text style={styles.insightPattern}>
                  {insight.pattern.toUpperCase()}
                </Text>
                <Text style={styles.insightDate}>
                  {formatDate(insight.generationDate)}
                </Text>
              </View>
            </View>

            <View style={styles.insightSection}>
              <Text style={styles.sectionTitle}>Pattern Description</Text>
              <Text style={styles.sectionText}>
                {insight.patternDescription}
              </Text>
            </View>

            {insight.contributingFactors &&
              insight.contributingFactors.length > 0 && (
                <View style={styles.insightSection}>
                  <Text style={styles.sectionTitle}>Contributing Factors</Text>
                  {insight.contributingFactors.map((factor: string, i: number) => (
                    <View key={i} style={styles.listItem}>
                      <Icon name="circle-small" size={20} color="#667eea" />
                      <Text style={styles.listText}>{factor}</Text>
                    </View>
                  ))}
                </View>
              )}

            {insight.observations && insight.observations.length > 0 && (
              <View style={styles.insightSection}>
                <Text style={styles.sectionTitle}>Observations</Text>
                {insight.observations.map((obs: string, i: number) => (
                  <View key={i} style={styles.listItem}>
                    <Icon name="circle-small" size={20} color="#48bb78" />
                    <Text style={styles.listText}>{obs}</Text>
                  </View>
                ))}
              </View>
            )}
          </View>
        );
      })}
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
    fontSize: 24,
    fontWeight: '700',
    color: '#2d3748',
  },
  insightCard: {
    backgroundColor: '#ffffff',
    margin: 16,
    marginTop: 0,
    padding: 20,
    borderRadius: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#4299e1',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 8,
  },
  insightHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
    marginBottom: 20,
  },
  insightHeaderText: {
    flex: 1,
  },
  insightPattern: {
    fontSize: 18,
    fontWeight: '700',
    color: '#2d3748',
    marginBottom: 4,
  },
  insightDate: {
    fontSize: 14,
    color: '#718096',
  },
  insightSection: {
    marginTop: 16,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#4a5568',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 12,
  },
  sectionText: {
    fontSize: 15,
    color: '#2d3748',
    lineHeight: 22,
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  listText: {
    flex: 1,
    fontSize: 15,
    color: '#2d3748',
    lineHeight: 22,
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

export default InsightsScreen;
