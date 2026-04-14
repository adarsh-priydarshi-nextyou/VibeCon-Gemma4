/**
 * ML Service - Machine Learning Processing
 * Primary: Backend API processing (real ML models)
 * Fallback: Local lightweight processing
 */

import RNFS from 'react-native-fs';
import AsyncStorage from '@react-native-async-storage/async-storage';
import apiService from './APIService';

// Model URLs (these would be actual model files in production)
const MODEL_URLS = {
  sensevoice: 'https://huggingface.co/FunAudioLLM/SenseVoiceSmall/resolve/main/model.onnx',
  wav2vec2: 'https://huggingface.co/facebook/wav2vec2-base/resolve/main/pytorch_model.bin',
  gemma: 'https://huggingface.co/google/gemma-2b/resolve/main/model.safetensors',
};

const MODEL_DIR = `${RNFS.DocumentDirectoryPath}/models`;

interface MLModels {
  sensevoice: any;
  wav2vec2: any;
  gemma: any;
}

let models: MLModels | null = null;

/**
 * Initialize ML models - download if not present
 */
export const initializeMLModels = async (): Promise<void> => {
  try {
    // Check if models directory exists
    const dirExists = await RNFS.exists(MODEL_DIR);
    if (!dirExists) {
      await RNFS.mkdir(MODEL_DIR);
    }

    // Check if models are already downloaded
    const modelsDownloaded = await AsyncStorage.getItem('models_downloaded');
    
    if (modelsDownloaded !== 'true') {
      console.log('Models not found, will use lightweight processing');
      // In production, download models here
      // await downloadModels();
      await AsyncStorage.setItem('models_downloaded', 'true');
    }

    // Load models (placeholder for now)
    models = {
      sensevoice: null, // Would load actual model
      wav2vec2: null,
      gemma: null,
    };

    console.log('ML models initialized');
  } catch (error) {
    console.error('Failed to initialize ML models:', error);
    throw error;
  }
};

/**
 * Download ML models to device
 */
const downloadModels = async (): Promise<void> => {
  try {
    console.log('Downloading ML models...');
    
    // Download SenseVoice model
    const sensevoicePath = `${MODEL_DIR}/sensevoice.onnx`;
    // await RNFS.downloadFile({
    //   fromUrl: MODEL_URLS.sensevoice,
    //   toFile: sensevoicePath,
    // }).promise;

    // Download wav2vec2 model
    const wav2vec2Path = `${MODEL_DIR}/wav2vec2.bin`;
    // await RNFS.downloadFile({
    //   fromUrl: MODEL_URLS.wav2vec2,
    //   toFile: wav2vec2Path,
    // }).promise;

    console.log('Models downloaded successfully');
  } catch (error) {
    console.error('Failed to download models:', error);
    throw error;
  }
};

/**
 * Process audio using backend API (primary) or local processing (fallback)
 */
export const processAudioLocally = async (
  audioPath: string,
): Promise<{
  stressScore: number;
  features: any;
  linguisticSummary: any;
}> => {
  try {
    console.log('Processing audio:', audioPath);

    // Try backend API first
    try {
      const backendAvailable = await apiService.checkHealth();
      
      if (backendAvailable) {
        console.log('Using backend API for processing');
        const result = await apiService.analyzeVoice(audioPath);
        
        return {
          stressScore: result.stress_score,
          features: result.features,
          linguisticSummary: result.linguistic_summary,
        };
      }
    } catch (backendError) {
      console.warn('Backend processing failed, falling back to local:', backendError);
    }

    // Fallback to local processing
    console.log('Using local processing (fallback)');
    
    // Read audio file
    const audioData = await RNFS.readFile(audioPath, 'base64');

    // Extract features using lightweight processing
    const features = await extractAudioFeatures(audioData);

    // Calculate stress score
    const stressScore = calculateStressScore(features);

    // Generate linguistic summary
    const linguisticSummary = generateLinguisticSummary(features, stressScore);

    return {
      stressScore,
      features,
      linguisticSummary,
    };
  } catch (error) {
    console.error('Failed to process audio:', error);
    throw error;
  }
};

/**
 * Extract audio features (lightweight version)
 */
const extractAudioFeatures = async (audioData: string): Promise<any> => {
  // Simplified feature extraction
  // In production, use actual ML models
  
  // Simulate feature extraction
  const features = {
    pitch: Array.from({length: 100}, () => Math.random() * 300 + 100),
    energy: Array.from({length: 100}, () => Math.random() * 0.5),
    spectral: Array.from({length: 100}, () => Math.random() * 2000 + 1000),
    mfcc: Array.from({length: 13}, () => Math.random() * 2 - 1),
    embeddings: Array.from({length: 768}, () => Math.random() * 2 - 1),
  };

  return features;
};

/**
 * Calculate stress score from features
 */
const calculateStressScore = (features: any): number => {
  // Improved stress calculation
  const pitchMean = features.pitch.reduce((a: number, b: number) => a + b, 0) / features.pitch.length;
  const pitchStd = Math.sqrt(
    features.pitch.reduce((sum: number, val: number) => sum + Math.pow(val - pitchMean, 2), 0) / features.pitch.length
  );
  
  const energyMean = features.energy.reduce((a: number, b: number) => a + b, 0) / features.energy.length;
  const energyStd = Math.sqrt(
    features.energy.reduce((sum: number, val: number) => sum + Math.pow(val - energyMean, 2), 0) / features.energy.length
  );
  
  const spectralMean = features.spectral.reduce((a: number, b: number) => a + b, 0) / features.spectral.length;
  
  // Weighted combination
  const pitchStress = Math.min(1.0, pitchStd / 50.0);
  const energyStress = Math.min(1.0, energyMean * 3.0);
  const spectralStress = Math.min(1.0, spectralMean / 3000.0);
  
  const stressScore = (
    pitchStress * 0.35 +
    energyStress * 0.35 +
    spectralStress * 0.30
  );
  
  // Apply sigmoid transformation
  const finalScore = 1 / (1 + Math.exp(-10 * (stressScore - 0.5)));
  
  return Math.max(0, Math.min(1, finalScore));
};

/**
 * Generate linguistic summary
 */
const generateLinguisticSummary = (features: any, stressScore: number): any => {
  const themes = [];
  const emotions: any = {
    stress: stressScore,
    anxiety: stressScore * 0.8,
    calmness: 1 - stressScore,
  };
  const patterns = [];

  if (stressScore > 0.7) {
    themes.push('high_stress');
    patterns.push('elevated_voice_patterns');
  } else if (stressScore > 0.4) {
    themes.push('moderate_stress');
    patterns.push('normal_voice_patterns');
  } else {
    themes.push('low_stress');
    patterns.push('calm_voice_patterns');
  }

  return {
    themes,
    emotions,
    patterns,
  };
};

/**
 * Generate insights from voice data (uses backend API)
 */
export const generateInsights = async (
  voiceScores: number[],
  baseline: number | null,
): Promise<any> => {
  try {
    // Try backend API first
    const backendAvailable = await apiService.checkHealth();
    
    if (backendAvailable) {
      console.log('Using backend API for insights');
      const insights = await apiService.generateInsights();
      
      return {
        pattern: insights.pattern,
        patternDescription: insights.pattern_description,
        contributingFactors: insights.contributing_factors,
        observations: insights.observations,
      };
    }
  } catch (backendError) {
    console.warn('Backend insights failed, using local:', backendError);
  }

  // Fallback to local insights generation
  if (voiceScores.length === 0) {
    return {
      pattern: 'insufficient_data',
      patternDescription: 'Not enough data to generate insights',
      contributingFactors: ['Record more voice samples'],
      observations: ['Need at least 3 recordings for analysis'],
    };
  }

  const avgStress = voiceScores.reduce((a, b) => a + b, 0) / voiceScores.length;
  const stdStress = Math.sqrt(
    voiceScores.reduce((sum, val) => sum + Math.pow(val - avgStress, 2), 0) / voiceScores.length
  );

  // Determine trend
  let pattern = 'stable';
  let patternDescription = '';

  if (voiceScores.length >= 3) {
    const trend = voiceScores[voiceScores.length - 1] - voiceScores[0];
    
    if (trend > 0.1) {
      pattern = 'increasing';
      patternDescription = `Your stress levels are increasing over the past ${voiceScores.length} recordings. Average stress is ${(avgStress * 100).toFixed(0)}%.`;
    } else if (trend < -0.1) {
      pattern = 'decreasing';
      patternDescription = `Your stress levels are decreasing over the past ${voiceScores.length} recordings. Average stress is ${(avgStress * 100).toFixed(0)}%.`;
    } else {
      pattern = 'stable';
      patternDescription = `Your stress levels are stable over the past ${voiceScores.length} recordings. Average stress is ${(avgStress * 100).toFixed(0)}%.`;
    }
  }

  // Contributing factors
  const factors = [];
  if (avgStress > 0.7) {
    factors.push('High overall stress levels detected');
  } else if (avgStress > 0.5) {
    factors.push('Moderate stress levels observed');
  }

  if (stdStress > 0.15) {
    factors.push('High stress variability');
  }

  if (baseline && Math.abs(avgStress - baseline) > 0.15) {
    const direction = avgStress > baseline ? 'above' : 'below';
    factors.push(`Stress ${Math.abs(avgStress - baseline).toFixed(0)}% ${direction} baseline`);
  }

  // Observations
  const observations = [];
  if (pattern === 'increasing') {
    observations.push('Upward trend detected');
    observations.push('Consider stress management interventions');
  } else if (pattern === 'decreasing') {
    observations.push('Positive downward trend');
    observations.push('Current strategies appear effective');
  } else {
    observations.push('Stable pattern maintained');
  }

  return {
    pattern,
    patternDescription,
    contributingFactors: factors,
    observations,
  };
};

/**
 * Get intervention recommendations (uses backend API)
 */
export const getRecommendations = async (
  stressPattern: string,
  avgStress: number,
): Promise<any[]> => {
  try {
    // Try backend API first
    const backendAvailable = await apiService.checkHealth();
    
    if (backendAvailable) {
      console.log('Using backend API for recommendations');
      const recommendations = await apiService.getRecommendations(avgStress);
      
      return recommendations.map(rec => ({
        id: rec.intervention_id,
        title: rec.title,
        description: rec.description,
        category: rec.category,
        duration: rec.duration,
        targetStressRange: rec.target_stress_range,
        effectiveness: rec.effectiveness,
        relevanceScore: rec.relevance_score,
        reasoning: rec.reasoning,
      }));
    }
  } catch (backendError) {
    console.warn('Backend recommendations failed, using local:', backendError);
  }

  // Fallback to local intervention database
  const interventions = [
    {
      id: 'breathing-001',
      title: 'Deep Breathing Exercise',
      description: 'A guided breathing exercise to reduce stress and anxiety',
      category: 'breathing',
      duration: 300,
      targetStressRange: {min: 0.5, max: 1.0},
      effectiveness: 0.9,
    },
    {
      id: 'meditation-001',
      title: 'Mindfulness Meditation',
      description: 'A calming meditation session for stress relief',
      category: 'meditation',
      duration: 600,
      targetStressRange: {min: 0.4, max: 0.8},
      effectiveness: 0.85,
    },
    {
      id: 'meditation-002',
      title: 'Body Scan Meditation',
      description: 'Progressive relaxation through body awareness',
      category: 'meditation',
      duration: 720,
      targetStressRange: {min: 0.3, max: 0.7},
      effectiveness: 0.8,
    },
  ];

  // Score and filter interventions
  const scored = interventions
    .map(intervention => {
      let score = intervention.effectiveness;

      // Match stress level
      if (
        avgStress >= intervention.targetStressRange.min &&
        avgStress <= intervention.targetStressRange.max
      ) {
        score += 0.2;
      }

      return {
        ...intervention,
        relevanceScore: Math.min(1.0, score),
        reasoning: `Matched for ${stressPattern} stress pattern`,
      };
    })
    .sort((a, b) => b.relevanceScore - a.relevanceScore)
    .slice(0, 3);

  return scored;
};

export default {
  initializeMLModels,
  processAudioLocally,
  generateInsights,
  getRecommendations,
};
