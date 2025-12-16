// User types
export interface User {
  id: string;
  email: string;
  display_name: string | null;
  created_at: string;
  is_active: boolean;
  is_premium: boolean;
  subscription_tier: string;
  has_adhd: boolean;
  has_autism_spectrum: boolean;
  has_anxiety: boolean;
  has_depression: boolean;
  other_conditions: string[];
  age_range: string | null;
  timezone: string;
  data_sharing_consent: boolean;
  research_participation: boolean;
}

export interface UserPreferences {
  id: string;
  user_id: string;
  theme: string;
  font_family: string;
  font_size: number;
  animation_speed: string;
  high_contrast: boolean;
  sound_enabled: boolean;
  haptic_feedback: boolean;
  notification_sound: string;
  reduce_motion: boolean;
  preferred_language: string;
  communication_style: string;
  morning_checkin_enabled: boolean;
  morning_checkin_time: string;
  evening_reflection_enabled: boolean;
  evening_reflection_time: string;
  max_notifications_per_day: number;
  time_blindness_support: boolean;
  task_breakdown_auto: boolean;
  sensory_load_tracking: boolean;
  routine_deviation_alerts: boolean;
  emotion_scaffolding_level: number;
}

// Auth types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  display_name?: string;
  has_adhd: boolean;
  has_autism_spectrum: boolean;
  has_anxiety: boolean;
  has_depression: boolean;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// Check-in types
export interface CheckinCreate {
  mood_score: number;
  energy_level: number;
  anxiety_level?: number;
  stress_level?: number;
  emotion_tags: string[];
  context_location?: string;
  context_activity?: string;
  context_social?: string;
  journal_text?: string;
  body_scan_data?: Record<string, any>;
  sensory_load_score?: number;
  executive_function_score?: number;
  masking_level?: number;
}

export interface Checkin {
  id: string;
  user_id: string;
  created_at: string;
  mood_score: number;
  energy_level: number;
  anxiety_level: number | null;
  stress_level: number | null;
  emotion_tags: string[];
  context_location: string | null;
  context_activity: string | null;
  context_social: string | null;
  journal_text: string | null;
  body_scan_data: Record<string, any> | null;
  sensory_load_score: number | null;
  executive_function_score: number | null;
  masking_level: number | null;
  ai_emotion_primary: string | null;
  ai_emotion_secondary: string | null;
  ai_confidence_score: number | null;
  crisis_risk_score: number;
  crisis_flagged: boolean;
}

export interface CheckinStats {
  streak_length: number;
  average_mood_7_days: number | null;
  average_mood_30_days: number | null;
  mood_trend: string;
  total_checkins: number;
}

// Intervention types
export interface Intervention {
  id: string;
  name: string;
  short_description: string;
  detailed_instructions: string;
  duration_seconds: number;
  effort_level: string;
  energy_required: string;
  therapeutic_approach: string;
  sub_category: string | null;
  target_emotions: string[];
  is_active: boolean;
  is_premium: boolean;
  media_type: string | null;
  media_url: string | null;
  adhd_friendly: boolean;
  asd_friendly: boolean;
  sensory_intensity: string;
  requires_verbal: boolean;
  requires_movement: boolean;
  contraindications: string[];
  age_appropriate: string[];
  evidence_source: string | null;
  evidence_strength: string | null;
  global_effectiveness_score: number;
  total_completions: number;
  average_rating: number;
}

export interface Recommendation {
  intervention_id: string;
  name: string;
  short_description: string;
  duration_seconds: number;
  effort_level: string;
  why_recommended: string;
  predicted_effectiveness: number;
}

export interface InterventionSession {
  id: string;
  intervention_id: string;
  checkin_id: string | null;
  started_at: string;
  completed_at: string | null;
  was_completed: boolean;
  effectiveness_rating: number | null;
  feedback_tags: string[];
  feedback_text: string | null;
}

// Crisis types
export interface CrisisResources {
  hotlines: {
    name: string;
    number: string;
    description: string;
    type: string;
  }[];
  message: string;
  safe_now_options: string[];
}

// API Response types
export interface CheckinResponse {
  checkin: Checkin;
  recommendations: Recommendation[];
  crisis_alert: boolean;
  crisis_resources: CrisisResources | null;
}

// ML and Insights types
export interface MLModelInfo {
  user_id: string;
  model_version: number;
  total_interactions: number;
  last_model_update: string | null;
  patterns_available: string[];
}

export interface MoodPrediction {
  prediction_available: boolean;
  predicted_mood?: number;
  predicted_energy?: number;
  prediction_time?: string;
  confidence?: number;
  trend_direction?: string;
  insights: string[];
  based_on_checkins?: number;
  reason?: string;
}

export interface DayForecast {
  date: string;
  day: string;
  periods: {
    morning?: { time: string; predicted_mood: number };
    afternoon?: { time: string; predicted_mood: number };
    evening?: { time: string; predicted_mood: number };
  };
}

export interface PatternDetection {
  patterns_detected: boolean;
  weekly_cycle?: {
    best_day: string;
    worst_day: string;
    spread: number;
    strength: string;
  };
  time_of_day_effect?: {
    best_time: string;
    worst_time: string;
    spread: number;
  };
  volatility?: {
    average_change: number;
    level: string;
  };
  recent_stability?: {
    recent_average: number;
    historical_average: number;
    change: number;
    direction: string;
  };
  notable_patterns: string[];
  reason?: string;
}

export interface CrisisRiskAssessment {
  risk_assessment_available: boolean;
  risk_level?: string;
  risk_score?: number;
  risk_factors: string[];
  recommendations: string[];
  assessed_at?: string;
  reason?: string;
}

export interface DailyInsight {
  insight: string;
  type: string;
  priority?: number;
}

export interface Achievement {
  name: string;
  description: string;
  icon: string;
}

export interface WeeklyInsights {
  period: string;
  generated_at: string;
  checkin_summary: {
    total: number;
    average_mood?: number;
    average_energy?: number;
    highest_mood?: number;
    lowest_mood?: number;
    consistency?: string;
    message?: string;
  };
  mood_insights: string[];
  intervention_insights: string[];
  personalized_tips: string[];
  achievements: Achievement[];
  focus_areas: string[];
}

export interface InterventionEffectivenessItem {
  intervention_id: string;
  average_rating: number;
  total_uses: number;
  best_for_emotion: string;
  consistency: number;
}

export interface InterventionEffectivenessReport {
  report_available: boolean;
  total_interventions_tried?: number;
  total_sessions?: number;
  top_interventions: InterventionEffectivenessItem[];
  least_effective: InterventionEffectivenessItem[];
  recommendation?: string;
  reason?: string;
}

export interface ComprehensiveReport {
  report_generated_at: string;
  model_version: number;
  total_interactions_learned: number;
  last_model_update: string | null;
  sections: {
    weekly_summary: WeeklyInsights;
    mood_patterns: PatternDetection;
    crisis_risk_assessment: CrisisRiskAssessment;
    optimal_intervention_times: any;
    intervention_effectiveness: InterventionEffectivenessReport;
  };
  key_insights: string[];
}
