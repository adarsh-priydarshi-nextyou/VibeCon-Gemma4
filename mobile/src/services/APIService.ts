/**
 * API Service - Backend Integration
 * Connects mobile app to FastAPI backend for real ML processing
 */

import axios, {AxiosInstance} from 'axios';
import RNFS from 'react-native-fs';
import {getAPIBaseURL} from '../config/api.config';

// Backend API URL from config
const API_BASE_URL = getAPIBaseURL();

interface VoiceAnalysisResponse {
  analysis_id: string;
  user_id: string;
  timestamp: string;
  stress_score: number;
  features: {
    pitch: number[];
    energy: number[];
    spectral: number[];
    mfcc: number[];
    embeddings: number[];
  };
  linguistic_summary: {
    themes: string[];
    emotions: Record<string, number>;
    patterns: string[];
  };
  audio_duration: number;
}

interface BaselineResponse {
  user_id: string;
  calculation_date: string;
  baseline_stress: number;
  data_points_used: number;
}

interface InsightResponse {
  insight_id: string;
  user_id: string;
  generation_date: string;
  pattern: string;
  pattern_description: string;
  contributing_factors: string[];
  observations: string[];
}

interface InterventionResponse {
  intervention_id: string;
  title: string;
  description: string;
  category: string;
  duration: number;
  audio_url: string;
  target_stress_range: {
    min: number;
    max: number;
  };
  effectiveness: number;
  relevance_score: number;
  reasoning: string;
}

class APIService {
  private client: AxiosInstance;
  private userId: string;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Generate or retrieve user ID
    this.userId = `mobile-user-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
  }

  /**
   * Set user ID
   */
  setUserId(userId: string) {
    this.userId = userId;
  }

  /**
   * Get user ID
   */
  getUserId(): string {
    return this.userId;
  }

  /**
   * Check if backend is reachable
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch (error) {
      console.error('Backend health check failed:', error);
      return false;
    }
  }

  /**
   * Upload and analyze voice sample
   */
  async analyzeVoice(audioPath: string): Promise<VoiceAnalysisResponse> {
    try {
      // Read audio file as base64
      const audioData = await RNFS.readFile(audioPath, 'base64');

      // Get file stats for duration
      const stats = await RNFS.stat(audioPath);
      const audioDuration = Math.floor(stats.size / 16000); // Approximate duration

      // Send to backend
      const response = await this.client.post('/audio/analyze', {
        user_id: this.userId,
        audio_data: audioData,
        audio_duration: audioDuration,
        timestamp: new Date().toISOString(),
      });

      return response.data;
    } catch (error: any) {
      console.error('Voice analysis failed:', error.response?.data || error.message);
      throw new Error('Failed to analyze voice. Please check your connection.');
    }
  }

  /**
   * Get user's baseline
   */
  async getBaseline(): Promise<BaselineResponse | null> {
    try {
      const response = await this.client.get(`/audio/baseline/${this.userId}`);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null; // No baseline yet
      }
      console.error('Failed to get baseline:', error.response?.data || error.message);
      throw new Error('Failed to get baseline');
    }
  }

  /**
   * Get insights for user
   */
  async getInsights(): Promise<InsightResponse[]> {
    try {
      const response = await this.client.get(`/insights/${this.userId}`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get insights:', error.response?.data || error.message);
      return [];
    }
  }

  /**
   * Generate new insights
   */
  async generateInsights(): Promise<InsightResponse> {
    try {
      const response = await this.client.post('/insights/generate', {
        user_id: this.userId,
      });
      return response.data;
    } catch (error: any) {
      console.error('Failed to generate insights:', error.response?.data || error.message);
      throw new Error('Failed to generate insights');
    }
  }

  /**
   * Get intervention recommendations
   */
  async getRecommendations(
    stressLevel?: number,
  ): Promise<InterventionResponse[]> {
    try {
      const params: any = {user_id: this.userId};
      if (stressLevel !== undefined) {
        params.stress_level = stressLevel;
      }

      const response = await this.client.get('/interventions/recommend', {
        params,
      });
      return response.data;
    } catch (error: any) {
      console.error('Failed to get recommendations:', error.response?.data || error.message);
      return [];
    }
  }

  /**
   * Get all interventions
   */
  async getAllInterventions(): Promise<InterventionResponse[]> {
    try {
      const response = await this.client.get('/interventions/');
      return response.data;
    } catch (error: any) {
      console.error('Failed to get interventions:', error.response?.data || error.message);
      return [];
    }
  }

  /**
   * Record telemetry for intervention playback
   */
  async recordTelemetry(data: {
    audio_id: string;
    play_duration: number;
    total_duration: number;
    completed: boolean;
    like_status?: boolean;
  }): Promise<void> {
    try {
      await this.client.post('/telemetry/record', {
        user_id: this.userId,
        timestamp: new Date().toISOString(),
        ...data,
      });
    } catch (error: any) {
      console.error('Failed to record telemetry:', error.response?.data || error.message);
      // Don't throw - telemetry is non-critical
    }
  }

  /**
   * Get user statistics
   */
  async getStatistics(): Promise<{
    total_recordings: number;
    avg_stress: number;
    trend: string;
  }> {
    try {
      const response = await this.client.get(`/audio/stats/${this.userId}`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to get statistics:', error.response?.data || error.message);
      return {
        total_recordings: 0,
        avg_stress: 0,
        trend: 'stable',
      };
    }
  }

  /**
   * Get recent voice analyses
   */
  async getRecentAnalyses(days: number = 7): Promise<VoiceAnalysisResponse[]> {
    try {
      const response = await this.client.get(`/audio/recent/${this.userId}`, {
        params: {days},
      });
      return response.data;
    } catch (error: any) {
      console.error('Failed to get recent analyses:', error.response?.data || error.message);
      return [];
    }
  }
}

// Export singleton instance
export const apiService = new APIService();

export default apiService;
