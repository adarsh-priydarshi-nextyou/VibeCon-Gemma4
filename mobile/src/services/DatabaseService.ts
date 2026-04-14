/**
 * Database Service - Local SQLite Database
 * Stores all data locally on device
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

interface VoiceAnalysis {
  id: string;
  userId: string;
  timestamp: string;
  stressScore: number;
  features: any;
  linguisticSummary: any;
  audioDuration: number;
}

interface Baseline {
  userId: string;
  calculationDate: string;
  baselineStress: number;
  dataPointsUsed: number;
}

interface Insight {
  id: string;
  userId: string;
  generationDate: string;
  pattern: string;
  patternDescription: string;
  contributingFactors: string[];
  observations: string[];
}

interface Telemetry {
  id: string;
  userId: string;
  audioId: string;
  timestamp: string;
  playDuration: number;
  totalDuration: number;
  completed: boolean;
  likeStatus: boolean | null;
}

const STORAGE_KEYS = {
  VOICE_ANALYSES: 'voice_analyses',
  BASELINES: 'baselines',
  INSIGHTS: 'insights',
  TELEMETRY: 'telemetry',
  USER_ID: 'user_id',
};

/**
 * Initialize database
 */
export const initializeDatabase = async (): Promise<void> => {
  try {
    // Check if user ID exists, create if not
    let userId = await AsyncStorage.getItem(STORAGE_KEYS.USER_ID);
    if (!userId) {
      userId = `mobile-user-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
      await AsyncStorage.setItem(STORAGE_KEYS.USER_ID, userId);
    }

    // Initialize storage arrays if they don't exist
    const keys = [
      STORAGE_KEYS.VOICE_ANALYSES,
      STORAGE_KEYS.BASELINES,
      STORAGE_KEYS.INSIGHTS,
      STORAGE_KEYS.TELEMETRY,
    ];

    for (const key of keys) {
      const exists = await AsyncStorage.getItem(key);
      if (!exists) {
        await AsyncStorage.setItem(key, JSON.stringify([]));
      }
    }

    console.log('Database initialized');
  } catch (error) {
    console.error('Failed to initialize database:', error);
    throw error;
  }
};

/**
 * Get user ID
 */
export const getUserId = async (): Promise<string> => {
  const userId = await AsyncStorage.getItem(STORAGE_KEYS.USER_ID);
  return userId || '';
};

/**
 * Store voice analysis
 */
export const storeVoiceAnalysis = async (
  analysis: Omit<VoiceAnalysis, 'id' | 'userId'>,
): Promise<string> => {
  try {
    const userId = await getUserId();
    const id = `analysis-${Date.now()}`;

    const voiceAnalysis: VoiceAnalysis = {
      id,
      userId,
      ...analysis,
    };

    const analyses = await getVoiceAnalyses();
    analyses.push(voiceAnalysis);
    await AsyncStorage.setItem(
      STORAGE_KEYS.VOICE_ANALYSES,
      JSON.stringify(analyses),
    );

    // Calculate and store baseline
    await calculateAndStoreBaseline();

    return id;
  } catch (error) {
    console.error('Failed to store voice analysis:', error);
    throw error;
  }
};

/**
 * Get voice analyses
 */
export const getVoiceAnalyses = async (): Promise<VoiceAnalysis[]> => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.VOICE_ANALYSES);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Failed to get voice analyses:', error);
    return [];
  }
};

/**
 * Get recent voice scores
 */
export const getRecentVoiceScores = async (
  days: number = 7,
): Promise<number[]> => {
  try {
    const analyses = await getVoiceAnalyses();
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);

    const recentAnalyses = analyses.filter(
      a => new Date(a.timestamp) >= cutoffDate,
    );

    return recentAnalyses.map(a => a.stressScore);
  } catch (error) {
    console.error('Failed to get recent voice scores:', error);
    return [];
  }
};

/**
 * Calculate and store baseline
 */
export const calculateAndStoreBaseline = async (): Promise<void> => {
  try {
    const userId = await getUserId();
    const voiceScores = await getRecentVoiceScores(7);

    if (voiceScores.length < 3) {
      console.log('Not enough data for baseline calculation');
      return;
    }

    // Calculate baseline with exponential decay
    const weights = voiceScores.map((_, i) =>
      Math.exp(-0.1 * (voiceScores.length - 1 - i)),
    );
    const totalWeight = weights.reduce((a, b) => a + b, 0);
    const baselineStress =
      voiceScores.reduce((sum, score, i) => sum + score * weights[i], 0) /
      totalWeight;

    const baseline: Baseline = {
      userId,
      calculationDate: new Date().toISOString(),
      baselineStress,
      dataPointsUsed: voiceScores.length,
    };

    await AsyncStorage.setItem(STORAGE_KEYS.BASELINES, JSON.stringify(baseline));
    console.log('Baseline calculated:', baselineStress);
  } catch (error) {
    console.error('Failed to calculate baseline:', error);
  }
};

/**
 * Get latest baseline
 */
export const getLatestBaseline = async (): Promise<Baseline | null> => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.BASELINES);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('Failed to get baseline:', error);
    return null;
  }
};

/**
 * Store insight
 */
export const storeInsight = async (
  insight: Omit<Insight, 'id' | 'userId'>,
): Promise<string> => {
  try {
    const userId = await getUserId();
    const id = `insight-${Date.now()}`;

    const newInsight: Insight = {
      id,
      userId,
      ...insight,
    };

    const insights = await getInsights();
    insights.push(newInsight);
    
    // Keep only last 10 insights
    const recentInsights = insights.slice(-10);
    
    await AsyncStorage.setItem(
      STORAGE_KEYS.INSIGHTS,
      JSON.stringify(recentInsights),
    );

    return id;
  } catch (error) {
    console.error('Failed to store insight:', error);
    throw error;
  }
};

/**
 * Get insights
 */
export const getInsights = async (): Promise<Insight[]> => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.INSIGHTS);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Failed to get insights:', error);
    return [];
  }
};

/**
 * Store telemetry
 */
export const storeTelemetry = async (
  telemetry: Omit<Telemetry, 'id' | 'userId'>,
): Promise<string> => {
  try {
    const userId = await getUserId();
    const id = `telemetry-${Date.now()}`;

    const newTelemetry: Telemetry = {
      id,
      userId,
      ...telemetry,
    };

    const telemetries = await getTelemetry();
    telemetries.push(newTelemetry);
    await AsyncStorage.setItem(
      STORAGE_KEYS.TELEMETRY,
      JSON.stringify(telemetries),
    );

    return id;
  } catch (error) {
    console.error('Failed to store telemetry:', error);
    throw error;
  }
};

/**
 * Get telemetry
 */
export const getTelemetry = async (): Promise<Telemetry[]> => {
  try {
    const data = await AsyncStorage.getItem(STORAGE_KEYS.TELEMETRY);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Failed to get telemetry:', error);
    return [];
  }
};

/**
 * Clear all data (for testing)
 */
export const clearAllData = async (): Promise<void> => {
  try {
    await AsyncStorage.multiRemove([
      STORAGE_KEYS.VOICE_ANALYSES,
      STORAGE_KEYS.BASELINES,
      STORAGE_KEYS.INSIGHTS,
      STORAGE_KEYS.TELEMETRY,
    ]);
    console.log('All data cleared');
  } catch (error) {
    console.error('Failed to clear data:', error);
    throw error;
  }
};

/**
 * Get statistics
 */
export const getStatistics = async (): Promise<{
  totalRecordings: number;
  avgStress: number;
  trend: string;
}> => {
  try {
    const analyses = await getVoiceAnalyses();
    const totalRecordings = analyses.length;
    
    if (totalRecordings === 0) {
      return {totalRecordings: 0, avgStress: 0, trend: 'stable'};
    }

    const avgStress =
      analyses.reduce((sum, a) => sum + a.stressScore, 0) / totalRecordings;

    // Determine trend
    let trend = 'stable';
    if (totalRecordings >= 3) {
      const recent = analyses.slice(-3);
      const trendValue = recent[recent.length - 1].stressScore - recent[0].stressScore;
      
      if (trendValue > 0.1) {
        trend = 'increasing';
      } else if (trendValue < -0.1) {
        trend = 'decreasing';
      }
    }

    return {totalRecordings, avgStress, trend};
  } catch (error) {
    console.error('Failed to get statistics:', error);
    return {totalRecordings: 0, avgStress: 0, trend: 'stable'};
  }
};

export default {
  initializeDatabase,
  getUserId,
  storeVoiceAnalysis,
  getVoiceAnalyses,
  getRecentVoiceScores,
  calculateAndStoreBaseline,
  getLatestBaseline,
  storeInsight,
  getInsights,
  storeTelemetry,
  getTelemetry,
  clearAllData,
  getStatistics,
};
