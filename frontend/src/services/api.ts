import axios, { type AxiosInstance, type AxiosError } from 'axios';
import type {
  AuthTokens,
  LoginRequest,
  RegisterRequest,
  User,
  UserPreferences,
  CheckinCreate,
  CheckinResponse,
  Checkin,
  CheckinStats,
  Intervention,
  Recommendation,
  CrisisResources,
  MLModelInfo,
  MoodPrediction,
  DayForecast,
  PatternDetection,
  CrisisRiskAssessment,
  DailyInsight,
  WeeklyInsights,
  InterventionEffectivenessReport,
  ComprehensiveReport,
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any;
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await this.refreshToken(refreshToken);
              localStorage.setItem('access_token', response.access_token);
              localStorage.setItem('refresh_token', response.refresh_token);
              originalRequest.headers.Authorization = `Bearer ${response.access_token}`;
              return this.api(originalRequest);
            }
          } catch (refreshError) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async register(data: RegisterRequest): Promise<User> {
    const response = await this.api.post('/auth/register', data);
    return response.data;
  }

  async login(data: LoginRequest): Promise<AuthTokens> {
    const response = await this.api.post('/auth/login', data);
    return response.data;
  }

  async refreshToken(refresh_token: string): Promise<AuthTokens> {
    const response = await this.api.post('/auth/refresh', { refresh_token });
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get('/auth/me');
    return response.data;
  }

  async logout(): Promise<void> {
    await this.api.post('/auth/logout');
  }

  // User endpoints
  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await this.api.patch('/users/me', data);
    return response.data;
  }

  async getPreferences(): Promise<UserPreferences> {
    const response = await this.api.get('/users/me/preferences');
    return response.data;
  }

  async updatePreferences(data: Partial<UserPreferences>): Promise<UserPreferences> {
    const response = await this.api.put('/users/me/preferences', data);
    return response.data;
  }

  async exportData(): Promise<any> {
    const response = await this.api.get('/users/me/export');
    return response.data;
  }

  async deleteAccount(): Promise<void> {
    await this.api.delete('/users/me');
  }

  // Check-in endpoints
  async createCheckin(data: CheckinCreate): Promise<CheckinResponse> {
    const response = await this.api.post('/checkins/', data);
    return response.data;
  }

  async getCheckins(page = 1, pageSize = 30): Promise<{ checkins: Checkin[]; total: number }> {
    const response = await this.api.get('/checkins/', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  }

  async getCheckinStats(): Promise<CheckinStats> {
    const response = await this.api.get('/checkins/stats');
    return response.data;
  }

  async getCheckin(id: string): Promise<Checkin> {
    const response = await this.api.get(`/checkins/${id}`);
    return response.data;
  }

  // Intervention endpoints
  async getInterventions(filters?: {
    therapeutic_approach?: string;
    max_duration_seconds?: number;
    target_emotion?: string;
    adhd_friendly?: boolean;
    asd_friendly?: boolean;
  }): Promise<Intervention[]> {
    const response = await this.api.get('/interventions/', { params: filters });
    return response.data;
  }

  async getIntervention(id: string): Promise<Intervention> {
    const response = await this.api.get(`/interventions/${id}`);
    return response.data;
  }

  async getRecommendations(data: {
    current_emotion: string;
    energy_level: number;
    time_available_minutes: number;
    context?: string;
  }): Promise<{ recommendations: Recommendation[] }> {
    const response = await this.api.post('/interventions/recommendations', data);
    return response.data;
  }

  async startSession(data: {
    intervention_id: string;
    checkin_id?: string;
    started_at: string;
    context_emotion?: string;
    context_energy_level?: number;
  }): Promise<any> {
    const response = await this.api.post('/interventions/sessions', data);
    return response.data;
  }

  async completeSession(
    sessionId: string,
    data: {
      completed_at: string;
      was_completed: boolean;
      effectiveness_rating?: number;
      feedback_tags?: string[];
      feedback_text?: string;
    }
  ): Promise<any> {
    const response = await this.api.post(`/interventions/sessions/${sessionId}/complete`, data);
    return response.data;
  }

  async skipSession(sessionId: string): Promise<any> {
    const response = await this.api.post(`/interventions/sessions/${sessionId}/skip`);
    return response.data;
  }

  async getEffectiveInterventions(): Promise<any> {
    const response = await this.api.get('/interventions/effective');
    return response.data;
  }

  // Crisis endpoints
  async getCrisisResources(): Promise<CrisisResources> {
    const response = await this.api.get('/crisis/resources');
    return response.data;
  }

  async reportCrisis(): Promise<any> {
    const response = await this.api.post('/crisis/report');
    return response.data;
  }

  async markSafe(): Promise<any> {
    const response = await this.api.post('/crisis/safe-now');
    return response.data;
  }

  async getSafetyPlan(): Promise<any> {
    const response = await this.api.get('/crisis/safety-plan');
    return response.data;
  }

  async updateSafetyPlan(data: any): Promise<any> {
    const response = await this.api.put('/crisis/safety-plan', data);
    return response.data;
  }

  // ML & Insights endpoints
  async getMLModelInfo(): Promise<MLModelInfo> {
    const response = await this.api.get('/ml/model/info');
    return response.data;
  }

  async trainModel(): Promise<any> {
    const response = await this.api.post('/ml/model/train');
    return response.data;
  }

  async getMoodPrediction(hoursAhead = 24): Promise<MoodPrediction> {
    const response = await this.api.get('/ml/predict/mood', {
      params: { hours_ahead: hoursAhead },
    });
    return response.data;
  }

  async getMoodForecast(days = 7): Promise<{ forecasts: DayForecast[]; generated_at: string }> {
    const response = await this.api.get('/ml/predict/forecast', {
      params: { days },
    });
    return response.data;
  }

  async getMoodPatterns(): Promise<PatternDetection> {
    const response = await this.api.get('/ml/patterns/mood');
    return response.data;
  }

  async getCircadianPatterns(): Promise<any> {
    const response = await this.api.get('/ml/patterns/circadian');
    return response.data;
  }

  async getTriggerPatterns(): Promise<any> {
    const response = await this.api.get('/ml/patterns/triggers');
    return response.data;
  }

  async getCrisisRiskAssessment(): Promise<CrisisRiskAssessment> {
    const response = await this.api.get('/ml/risk/crisis');
    return response.data;
  }

  async getOptimalInterventionTimes(): Promise<any> {
    const response = await this.api.get('/ml/optimal-times');
    return response.data;
  }

  async getDailyInsight(): Promise<DailyInsight> {
    const response = await this.api.get('/ml/insights/daily');
    return response.data;
  }

  async getWeeklyInsights(): Promise<WeeklyInsights> {
    const response = await this.api.get('/ml/insights/weekly');
    return response.data;
  }

  async getInterventionEffectiveness(): Promise<InterventionEffectivenessReport> {
    const response = await this.api.get('/ml/insights/effectiveness');
    return response.data;
  }

  async getComprehensiveReport(): Promise<ComprehensiveReport> {
    const response = await this.api.get('/ml/insights/comprehensive');
    return response.data;
  }

  async getCopingMap(): Promise<any> {
    const response = await this.api.get('/ml/coping-map');
    return response.data;
  }

  async getPersonalizedScore(
    interventionId: string,
    emotion: string,
    energyLevel = 5
  ): Promise<{ intervention_id: string; score: number; explanation: string }> {
    const response = await this.api.get('/ml/score/intervention', {
      params: {
        intervention_id: interventionId,
        emotion,
        energy_level: energyLevel,
      },
    });
    return response.data;
  }
}

export const api = new ApiService();
