# Firefly Technical Architecture
## Detailed Implementation Guide

---

## 1. SYSTEM ARCHITECTURE OVERVIEW

### 1.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│   React Web  │   React      │   React      │   Wearable        │
│   App (PWA)  │   Native iOS │   Native     │   SDKs            │
│              │              │   Android    │                   │
└──────┬───────┴──────┬───────┴──────┬───────┴─────────┬─────────┘
       │              │              │                 │
       └──────────────┴──────────────┴─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EDGE LAYER (CloudFlare)                      │
│  CDN | WAF | DDoS Protection | SSL Termination | Rate Limiting │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                            │
│                    (AWS API Gateway / Kong)                     │
│      Rate Limiting | Auth | Request Routing | Monitoring       │
└─────────────────────────────┬───────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   AUTH        │   │    CORE API     │   │    ML/AI        │
│   SERVICE     │   │    SERVICE      │   │    SERVICE      │
│   (OAuth2.0)  │   │   (Node.js)     │   │   (Python)      │
│               │   │                 │   │                 │
│ • JWT tokens  │   │ • User mgmt     │   │ • Emotion clf   │
│ • MFA         │   │ • Check-ins     │   │ • Recommend     │
│ • Session     │   │ • Interventions │   │ • NLP analysis  │
│ • OAuth flows │   │ • Feedback      │   │ • Crisis detect │
└───────┬───────┘   └────────┬────────┘   └────────┬────────┘
        │                    │                     │
        └────────────────────┼─────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                            │
│                    (Prisma ORM / SQLAlchemy)                    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  PostgreSQL   │   │     Redis       │   │  Elasticsearch  │
│  (Primary DB) │   │   (Cache)       │   │   (Search)      │
│               │   │                 │   │                 │
│ • User data   │   │ • Sessions      │   │ • Full-text     │
│ • Check-ins   │   │ • API cache     │   │ • Analytics     │
│ • Feedback    │   │ • Rate limits   │   │ • Audit logs    │
│ • Preferences │   │ • Real-time     │   │ • Search        │
└───────────────┘   └─────────────────┘   └─────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE & ML MODELS                          │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   AWS S3        │   ML Model       │   TimescaleDB              │
│   (Object)      │   Registry       │   (Time-series)            │
│                 │                  │                            │
│ • User uploads  │ • Emotion models │ • Mood trends              │
│ • Backups       │ • NLP models     │ • Biometric data           │
│ • Static assets │ • Version ctrl   │ • Pattern analysis         │
└─────────────────┴─────────────────┴─────────────────────────────┘
```

---

## 2. DATABASE SCHEMA

### 2.1 Core Tables

```sql
-- Users table with neurodiversity preferences
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    is_premium BOOLEAN DEFAULT FALSE,
    subscription_tier VARCHAR(50) DEFAULT 'free',

    -- Profile
    display_name VARCHAR(100),
    age_range VARCHAR(20), -- '18-24', '25-34', etc.
    timezone VARCHAR(50) DEFAULT 'UTC',

    -- Neurodiversity Preferences
    has_adhd BOOLEAN DEFAULT FALSE,
    has_autism_spectrum BOOLEAN DEFAULT FALSE,
    has_anxiety BOOLEAN DEFAULT FALSE,
    has_depression BOOLEAN DEFAULT FALSE,
    other_conditions TEXT[],

    -- Privacy Settings
    data_sharing_consent BOOLEAN DEFAULT FALSE,
    research_participation BOOLEAN DEFAULT FALSE,
    therapist_sharing_enabled BOOLEAN DEFAULT FALSE,

    -- Account Security
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,

    CONSTRAINT valid_subscription CHECK (
        subscription_tier IN ('free', 'premium', 'family', 'enterprise')
    )
);

-- User Preferences for personalization
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Visual Preferences
    theme VARCHAR(50) DEFAULT 'calm_light',
    font_family VARCHAR(50) DEFAULT 'Inter',
    font_size INTEGER DEFAULT 16,
    animation_speed VARCHAR(20) DEFAULT 'normal', -- 'none', 'slow', 'normal', 'fast'
    high_contrast BOOLEAN DEFAULT FALSE,

    -- Sensory Preferences
    sound_enabled BOOLEAN DEFAULT TRUE,
    haptic_feedback BOOLEAN DEFAULT TRUE,
    notification_sound VARCHAR(50) DEFAULT 'gentle_chime',
    reduce_motion BOOLEAN DEFAULT FALSE,

    -- Communication Preferences
    preferred_language VARCHAR(10) DEFAULT 'en',
    communication_style VARCHAR(50) DEFAULT 'warm', -- 'warm', 'direct', 'playful', 'professional'

    -- Notification Preferences
    morning_checkin_enabled BOOLEAN DEFAULT TRUE,
    morning_checkin_time TIME DEFAULT '08:00:00',
    evening_reflection_enabled BOOLEAN DEFAULT TRUE,
    evening_reflection_time TIME DEFAULT '20:00:00',
    max_notifications_per_day INTEGER DEFAULT 3,
    quiet_hours_start TIME DEFAULT '22:00:00',
    quiet_hours_end TIME DEFAULT '07:00:00',

    -- ADHD-Specific
    time_blindness_support BOOLEAN DEFAULT FALSE,
    task_breakdown_auto BOOLEAN DEFAULT FALSE,
    hyperfocus_reminders BOOLEAN DEFAULT FALSE,
    dopamine_reward_style VARCHAR(50) DEFAULT 'standard',

    -- Autism-Specific
    sensory_load_tracking BOOLEAN DEFAULT FALSE,
    routine_deviation_alerts BOOLEAN DEFAULT FALSE,
    emotion_scaffolding_level INTEGER DEFAULT 1, -- 1-3

    CONSTRAINT unique_user_preferences UNIQUE (user_id)
);

-- Daily mood check-ins
CREATE TABLE mood_checkins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Primary Mood Data
    mood_score INTEGER NOT NULL CHECK (mood_score BETWEEN 1 AND 10),
    energy_level INTEGER NOT NULL CHECK (energy_level BETWEEN 1 AND 10),
    anxiety_level INTEGER CHECK (anxiety_level BETWEEN 1 AND 10),
    stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 10),

    -- Emotion Tags (multiple selection)
    emotion_tags TEXT[] DEFAULT '{}',

    -- Context
    context_location VARCHAR(50), -- 'home', 'work', 'school', 'social', 'other'
    context_activity VARCHAR(100),
    context_social VARCHAR(50), -- 'alone', 'with_family', 'with_friends', 'with_coworkers'

    -- Optional Journal
    journal_text TEXT,
    journal_sentiment_score FLOAT,
    journal_emotion_classification JSONB,

    -- Voice Recording (if applicable)
    voice_recording_url TEXT,
    voice_sentiment_analysis JSONB,

    -- Body Scan (if used)
    body_scan_data JSONB, -- {area: tension_level}

    -- Neurodiversity-Specific
    sensory_load_score INTEGER, -- For ASD users
    executive_function_score INTEGER, -- For ADHD users
    masking_level INTEGER, -- How much masking today

    -- AI Analysis
    ai_emotion_primary VARCHAR(50),
    ai_emotion_secondary VARCHAR(50),
    ai_confidence_score FLOAT,
    crisis_risk_score FLOAT DEFAULT 0,
    crisis_flagged BOOLEAN DEFAULT FALSE,

    -- Indexing for time-series queries
    INDEX idx_user_checkins (user_id, created_at DESC),
    INDEX idx_crisis_flags (crisis_flagged, created_at DESC)
);

-- Micro-action library
CREATE TABLE interventions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    short_description TEXT NOT NULL,
    detailed_instructions TEXT NOT NULL,
    duration_seconds INTEGER NOT NULL,
    effort_level VARCHAR(20) NOT NULL, -- 'minimal', 'low', 'medium', 'high'
    energy_required VARCHAR(20) NOT NULL,

    -- Categorization
    therapeutic_approach VARCHAR(50) NOT NULL, -- 'DBT', 'ACT', 'CBT', 'Mindfulness', 'Sensory', 'Physical'
    sub_category VARCHAR(100),
    target_emotions TEXT[] NOT NULL DEFAULT '{}',

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    is_premium BOOLEAN DEFAULT FALSE,
    media_type VARCHAR(50), -- 'text', 'audio', 'video', 'interactive'
    media_url TEXT,

    -- Neurodiversity Tags
    adhd_friendly BOOLEAN DEFAULT TRUE,
    asd_friendly BOOLEAN DEFAULT TRUE,
    sensory_intensity VARCHAR(20) DEFAULT 'moderate',
    requires_verbal BOOLEAN DEFAULT FALSE,
    requires_movement BOOLEAN DEFAULT FALSE,

    -- Safety
    contraindications TEXT[],
    age_appropriate TEXT[] DEFAULT '{"18+"}',

    -- Evidence Base
    evidence_source TEXT,
    evidence_strength VARCHAR(20), -- 'strong', 'moderate', 'emerging'

    -- Global Effectiveness (updated periodically)
    global_effectiveness_score FLOAT DEFAULT 0.5,
    total_completions INTEGER DEFAULT 0,
    average_rating FLOAT DEFAULT 0,

    -- Full-text search
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('english', name || ' ' || short_description)
    ) STORED,

    INDEX idx_intervention_emotions USING gin (target_emotions),
    INDEX idx_search USING gin (search_vector)
);

-- User-intervention interaction tracking
CREATE TABLE intervention_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    intervention_id UUID NOT NULL REFERENCES interventions(id),
    checkin_id UUID REFERENCES mood_checkins(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Session Data
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_actual_seconds INTEGER,
    was_completed BOOLEAN DEFAULT FALSE,
    was_skipped BOOLEAN DEFAULT FALSE,

    -- User Feedback
    effectiveness_rating INTEGER CHECK (effectiveness_rating BETWEEN 1 AND 5),
    feedback_tags TEXT[],
    feedback_text TEXT,

    -- Context at time of recommendation
    context_emotion VARCHAR(50),
    context_energy_level INTEGER,
    context_time_of_day VARCHAR(20),

    -- AI Learning Data
    predicted_effectiveness FLOAT,
    actual_effectiveness FLOAT,
    learning_signal FLOAT, -- For bandit algorithm

    INDEX idx_user_sessions (user_id, created_at DESC),
    INDEX idx_intervention_stats (intervention_id, was_completed)
);

-- User's personalized model state
CREATE TABLE user_ml_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Recommendation Engine State
    bandit_model_state JSONB NOT NULL DEFAULT '{}',
    intervention_prior_beliefs JSONB NOT NULL DEFAULT '{}',

    -- Pattern Recognition
    circadian_patterns JSONB DEFAULT '{}',
    trigger_patterns JSONB DEFAULT '{}',
    coping_effectiveness_map JSONB DEFAULT '{}',

    -- Time blindness model (ADHD)
    time_estimation_bias FLOAT DEFAULT 0,
    task_completion_patterns JSONB DEFAULT '{}',

    -- Sensory patterns (ASD)
    sensory_sensitivity_profile JSONB DEFAULT '{}',
    regulation_strategy_preferences JSONB DEFAULT '{}',

    -- Model metadata
    total_interactions INTEGER DEFAULT 0,
    last_model_update TIMESTAMP WITH TIME ZONE,
    model_version VARCHAR(50) DEFAULT 'v1.0',

    CONSTRAINT unique_user_model UNIQUE (user_id)
);

-- Weekly summaries and insights
CREATE TABLE weekly_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    week_start_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Aggregated Stats
    total_checkins INTEGER DEFAULT 0,
    average_mood_score FLOAT,
    mood_trend VARCHAR(20), -- 'improving', 'stable', 'declining'
    average_energy_level FLOAT,

    -- Top Insights
    most_common_emotions TEXT[],
    most_effective_interventions TEXT[],
    recommended_focus_areas TEXT[],

    -- Patterns Discovered
    best_time_for_checkins VARCHAR(20),
    trigger_patterns_identified JSONB,
    coping_strategies_that_worked JSONB,

    -- Goals Progress
    streak_length INTEGER DEFAULT 0,
    interventions_completed INTEGER DEFAULT 0,
    skills_practiced TEXT[],

    -- AI-Generated Narrative
    summary_narrative TEXT,

    -- Gamification
    achievements_unlocked TEXT[],
    firefly_count INTEGER DEFAULT 0,

    CONSTRAINT unique_weekly_summary UNIQUE (user_id, week_start_date)
);

-- Crisis events and interventions
CREATE TABLE crisis_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Trigger Source
    trigger_source VARCHAR(50) NOT NULL, -- 'journal_nlp', 'checkin', 'user_reported'
    associated_checkin_id UUID REFERENCES mood_checkins(id),

    -- Risk Assessment
    risk_score FLOAT NOT NULL,
    risk_level VARCHAR(20) NOT NULL, -- 'low', 'moderate', 'high', 'critical'
    crisis_keywords_detected TEXT[],

    -- Response
    immediate_response_shown BOOLEAN DEFAULT TRUE,
    hotline_info_displayed BOOLEAN DEFAULT FALSE,
    safety_plan_accessed BOOLEAN DEFAULT FALSE,
    emergency_contact_notified BOOLEAN DEFAULT FALSE,

    -- Resolution
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,

    -- Follow-up
    follow_up_scheduled BOOLEAN DEFAULT FALSE,
    follow_up_completed BOOLEAN DEFAULT FALSE,

    INDEX idx_crisis_user (user_id, created_at DESC),
    INDEX idx_unresolved_crisis (resolved, created_at DESC)
);

-- User streaks and achievements
CREATE TABLE user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_type VARCHAR(100) NOT NULL,
    achieved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',

    CONSTRAINT unique_achievement UNIQUE (user_id, achievement_type)
);

-- Audit log for compliance
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id UUID REFERENCES users(id),
    action_type VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id UUID,
    ip_address INET,
    user_agent TEXT,
    request_details JSONB,
    response_status INTEGER,

    INDEX idx_audit_user (user_id, timestamp DESC),
    INDEX idx_audit_action (action_type, timestamp DESC)
);

-- Therapist portal access
CREATE TABLE therapist_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    therapist_email VARCHAR(255) NOT NULL,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,

    -- Permissions
    can_view_checkins BOOLEAN DEFAULT TRUE,
    can_view_journals BOOLEAN DEFAULT FALSE,
    can_view_interventions BOOLEAN DEFAULT TRUE,
    can_view_summaries BOOLEAN DEFAULT TRUE,

    last_accessed TIMESTAMP WITH TIME ZONE,

    CONSTRAINT unique_therapist_access UNIQUE (user_id, therapist_email)
);
```

### 2.2 Database Indexes and Performance

```sql
-- Composite indexes for common queries
CREATE INDEX idx_checkins_user_date ON mood_checkins(user_id, created_at DESC);
CREATE INDEX idx_checkins_crisis ON mood_checkins(crisis_flagged) WHERE crisis_flagged = TRUE;
CREATE INDEX idx_sessions_effectiveness ON intervention_sessions(intervention_id, was_completed, effectiveness_rating);
CREATE INDEX idx_user_active_premium ON users(is_active, is_premium) WHERE is_active = TRUE;

-- Partial indexes for performance
CREATE INDEX idx_recent_checkins ON mood_checkins(created_at DESC)
    WHERE created_at > NOW() - INTERVAL '30 days';

-- TimescaleDB hypertable for time-series data
SELECT create_hypertable('mood_checkins', 'created_at', migrate_data => true);

-- Retention policy (keep detailed data for 2 years, aggregate older)
SELECT add_retention_policy('mood_checkins', INTERVAL '2 years');
```

---

## 3. API SPECIFICATION

### 3.1 RESTful API Endpoints

```yaml
openapi: 3.0.3
info:
  title: Firefly Mental Wellness API
  version: 1.0.0
  description: API for the Firefly adaptive mental wellness platform

servers:
  - url: https://api.firefly.app/v1
    description: Production
  - url: https://api-staging.firefly.app/v1
    description: Staging

security:
  - BearerAuth: []

paths:
  # Authentication
  /auth/register:
    post:
      summary: Register new user
      tags: [Authentication]
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [email, password]
              properties:
                email:
                  type: string
                  format: email
                password:
                  type: string
                  minLength: 12
                display_name:
                  type: string
      responses:
        201:
          description: User created successfully
        400:
          description: Validation error
        409:
          description: Email already exists

  /auth/login:
    post:
      summary: User login
      tags: [Authentication]
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [email, password]
              properties:
                email:
                  type: string
                password:
                  type: string
                mfa_code:
                  type: string
      responses:
        200:
          description: Login successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  access_token:
                    type: string
                  refresh_token:
                    type: string
                  expires_in:
                    type: integer
        401:
          description: Invalid credentials

  # User Profile
  /users/me:
    get:
      summary: Get current user profile
      tags: [Users]
      responses:
        200:
          description: User profile
    patch:
      summary: Update user profile
      tags: [Users]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserUpdate'

  /users/me/preferences:
    get:
      summary: Get user preferences
      tags: [Users]
    put:
      summary: Update all preferences
      tags: [Users]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserPreferences'

  # Mood Check-ins
  /checkins:
    post:
      summary: Create new mood check-in
      tags: [Check-ins]
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CheckinCreate'
      responses:
        201:
          description: Check-in created
          content:
            application/json:
              schema:
                type: object
                properties:
                  checkin:
                    $ref: '#/components/schemas/Checkin'
                  recommendations:
                    type: array
                    items:
                      $ref: '#/components/schemas/InterventionRecommendation'
                  crisis_alert:
                    type: boolean
    get:
      summary: Get user's check-in history
      tags: [Check-ins]
      parameters:
        - name: start_date
          in: query
          schema:
            type: string
            format: date
        - name: end_date
          in: query
          schema:
            type: string
            format: date
        - name: limit
          in: query
          schema:
            type: integer
            default: 30
      responses:
        200:
          description: List of check-ins

  /checkins/{checkin_id}:
    get:
      summary: Get specific check-in
      tags: [Check-ins]
      parameters:
        - name: checkin_id
          in: path
          required: true
          schema:
            type: string
            format: uuid

  # Interventions
  /interventions:
    get:
      summary: Get intervention library
      tags: [Interventions]
      parameters:
        - name: therapeutic_approach
          in: query
          schema:
            type: string
        - name: duration_max
          in: query
          schema:
            type: integer
        - name: energy_level
          in: query
          schema:
            type: string
        - name: target_emotion
          in: query
          schema:
            type: string
      responses:
        200:
          description: List of interventions

  /interventions/recommendations:
    post:
      summary: Get personalized recommendations
      tags: [Interventions]
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                current_emotion:
                  type: string
                energy_level:
                  type: integer
                time_available_minutes:
                  type: integer
                context:
                  type: string
      responses:
        200:
          description: Top 3 recommendations

  /interventions/{intervention_id}/start:
    post:
      summary: Start an intervention session
      tags: [Interventions]
      parameters:
        - name: intervention_id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Session started

  /interventions/sessions/{session_id}/complete:
    post:
      summary: Complete intervention and provide feedback
      tags: [Interventions]
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                effectiveness_rating:
                  type: integer
                  minimum: 1
                  maximum: 5
                feedback_tags:
                  type: array
                  items:
                    type: string
                feedback_text:
                  type: string

  # Insights & Summaries
  /insights/weekly:
    get:
      summary: Get weekly summary
      tags: [Insights]
      parameters:
        - name: week_of
          in: query
          schema:
            type: string
            format: date

  /insights/patterns:
    get:
      summary: Get identified patterns
      tags: [Insights]
      responses:
        200:
          description: User patterns and trends

  /insights/achievements:
    get:
      summary: Get user achievements
      tags: [Insights]

  # Crisis Support
  /crisis/safety-plan:
    get:
      summary: Get user's safety plan
      tags: [Crisis]
    put:
      summary: Update safety plan
      tags: [Crisis]

  /crisis/report:
    post:
      summary: User self-reports crisis
      tags: [Crisis]

  # ADHD Tools
  /adhd/time-estimation:
    post:
      summary: Log time estimation for learning
      tags: [ADHD]
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                task_description:
                  type: string
                estimated_minutes:
                  type: integer
                actual_minutes:
                  type: integer

  /adhd/task-breakdown:
    post:
      summary: Get AI task breakdown
      tags: [ADHD]
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                task:
                  type: string
                max_steps:
                  type: integer
                  default: 10

  # ASD Tools
  /asd/sensory-load:
    post:
      summary: Log current sensory load
      tags: [ASD]
    get:
      summary: Get sensory load history
      tags: [ASD]

  /asd/routine:
    get:
      summary: Get daily routine
      tags: [ASD]
    put:
      summary: Update routine
      tags: [ASD]

  # Data Export
  /export/all:
    get:
      summary: Export all user data (GDPR/CCPA)
      tags: [Privacy]
      responses:
        200:
          description: Download link for data export

  /delete-account:
    delete:
      summary: Delete user account and all data
      tags: [Privacy]

components:
  schemas:
    CheckinCreate:
      type: object
      required: [mood_score, energy_level]
      properties:
        mood_score:
          type: integer
          minimum: 1
          maximum: 10
        energy_level:
          type: integer
          minimum: 1
          maximum: 10
        anxiety_level:
          type: integer
          minimum: 1
          maximum: 10
        stress_level:
          type: integer
          minimum: 1
          maximum: 10
        emotion_tags:
          type: array
          items:
            type: string
        journal_text:
          type: string
        context_location:
          type: string
        context_activity:
          type: string
        body_scan_data:
          type: object

    Checkin:
      allOf:
        - $ref: '#/components/schemas/CheckinCreate'
        - type: object
          properties:
            id:
              type: string
              format: uuid
            created_at:
              type: string
              format: date-time
            ai_emotion_primary:
              type: string
            ai_confidence_score:
              type: number

    InterventionRecommendation:
      type: object
      properties:
        intervention_id:
          type: string
        name:
          type: string
        short_description:
          type: string
        duration_seconds:
          type: integer
        effort_level:
          type: string
        why_recommended:
          type: string
        predicted_effectiveness:
          type: number

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

---

## 4. MICROSERVICES ARCHITECTURE

### 4.1 Service Breakdown

```
┌─────────────────────────────────────────────────────────────────┐
│                        FIREFLY SERVICES                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Auth      │     │   Core      │     │   ML/AI     │
│   Service   │     │   Service   │     │   Service   │
│             │     │             │     │             │
│ Port: 3001  │     │ Port: 3002  │     │ Port: 5001  │
│ Node.js     │     │ Node.js     │     │ Python      │
└─────────────┘     └─────────────┘     └─────────────┘

┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Notification│     │   Crisis    │     │  Analytics  │
│   Service   │     │   Service   │     │   Service   │
│             │     │             │     │             │
│ Port: 3003  │     │ Port: 3004  │     │ Port: 3005  │
│ Node.js     │     │ Node.js     │     │ Node.js     │
└─────────────┘     └─────────────┘     └─────────────┘

┌─────────────┐     ┌─────────────┐
│   Worker    │     │   Scheduler │
│   Service   │     │   Service   │
│             │     │             │
│ Background  │     │ Cron jobs   │
│ Bull queues │     │ Daily tasks │
└─────────────┘     └─────────────┘
```

### 4.2 Inter-Service Communication

```javascript
// Using RabbitMQ for event-driven architecture

// Example: Check-in Created Event
const EVENTS = {
  CHECKIN_CREATED: 'checkin.created',
  CRISIS_DETECTED: 'crisis.detected',
  INTERVENTION_COMPLETED: 'intervention.completed',
  MODEL_UPDATE_NEEDED: 'ml.model.update',
  WEEKLY_SUMMARY_DUE: 'summary.weekly.due',
};

// Publisher (Core Service)
async function publishCheckinCreated(checkin) {
  await rabbitMQ.publish(EVENTS.CHECKIN_CREATED, {
    userId: checkin.user_id,
    checkinId: checkin.id,
    journalText: checkin.journal_text,
    timestamp: checkin.created_at,
  });
}

// Consumer (ML Service)
async function handleCheckinCreated(message) {
  const { userId, checkinId, journalText } = message;

  // Analyze journal text for emotions and crisis
  const analysis = await emotionClassifier.analyze(journalText);

  // Update user's ML model
  await updateUserModel(userId, analysis);

  // Check for crisis indicators
  if (analysis.crisis_score > CRISIS_THRESHOLD) {
    await rabbitMQ.publish(EVENTS.CRISIS_DETECTED, {
      userId,
      checkinId,
      riskScore: analysis.crisis_score,
    });
  }
}
```

---

## 5. ML/AI PIPELINE

### 5.1 Emotion Classification Model

```python
# models/emotion_classifier.py

import torch
from transformers import BertTokenizer, BertModel
import torch.nn as nn

class EmotionClassifier(nn.Module):
    def __init__(self, num_emotions=12, hidden_size=768):
        super().__init__()
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        self.dropout = nn.Dropout(0.3)
        self.classifier = nn.Linear(hidden_size, num_emotions)

        # Freeze BERT layers initially (fine-tune later)
        for param in self.bert.parameters():
            param.requires_grad = False

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        pooled_output = outputs.pooler_output
        dropped = self.dropout(pooled_output)
        logits = self.classifier(dropped)
        return logits

    @torch.no_grad()
    def predict(self, text, tokenizer, device='cpu'):
        self.eval()
        inputs = tokenizer(
            text,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=512
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        logits = self.forward(
            inputs['input_ids'],
            inputs['attention_mask']
        )

        probabilities = torch.softmax(logits, dim=-1)
        return probabilities.cpu().numpy()

# Emotion labels
EMOTION_LABELS = [
    'joy', 'sadness', 'anger', 'fear', 'disgust', 'surprise',
    'anxiety', 'overwhelm', 'calm', 'hopeful', 'frustrated', 'neutral'
]
```

### 5.2 Recommendation Engine (Contextual Bandit)

```python
# models/recommendation_engine.py

import numpy as np
from scipy.stats import beta
from typing import List, Dict, Tuple

class ContextualThompsonSampling:
    """
    Contextual Multi-Armed Bandit using Thompson Sampling
    for personalized intervention recommendations.
    """

    def __init__(self, num_interventions: int, context_dim: int):
        self.num_interventions = num_interventions
        self.context_dim = context_dim

        # Prior beliefs (Beta distribution parameters)
        self.alpha = np.ones((num_interventions,))
        self.beta_param = np.ones((num_interventions,))

        # Context-specific weights
        self.weights = np.random.randn(num_interventions, context_dim) * 0.1
        self.learning_rate = 0.01

    def sample_reward(self) -> np.ndarray:
        """Sample expected rewards from posterior distribution."""
        return beta.rvs(self.alpha, self.beta_param)

    def get_context_score(self, context: np.ndarray) -> np.ndarray:
        """Calculate context-adjusted scores."""
        return np.dot(self.weights, context)

    def recommend(
        self,
        context: np.ndarray,
        available_interventions: List[int],
        top_k: int = 3
    ) -> List[Tuple[int, float]]:
        """
        Get top-k recommendations based on Thompson Sampling
        with contextual information.
        """
        # Sample from posterior
        sampled_rewards = self.sample_reward()

        # Add context influence
        context_scores = self.get_context_score(context)

        # Combined score
        combined_scores = sampled_rewards + 0.5 * context_scores

        # Filter to available interventions
        available_scores = [
            (idx, combined_scores[idx])
            for idx in available_interventions
        ]

        # Sort by score (descending)
        available_scores.sort(key=lambda x: x[1], reverse=True)

        # Ensure diversity (not all same category)
        return self._ensure_diversity(available_scores[:top_k * 2])[:top_k]

    def update(
        self,
        intervention_idx: int,
        context: np.ndarray,
        reward: float
    ):
        """
        Update model based on user feedback.

        reward: 0 (not helpful) to 1 (very helpful)
        """
        # Update Beta distribution parameters
        if reward > 0.5:  # Positive feedback
            self.alpha[intervention_idx] += reward
        else:  # Negative feedback
            self.beta_param[intervention_idx] += (1 - reward)

        # Update context weights (gradient descent)
        prediction = np.dot(self.weights[intervention_idx], context)
        error = reward - prediction
        self.weights[intervention_idx] += self.learning_rate * error * context

    def _ensure_diversity(
        self,
        scored_interventions: List[Tuple[int, float]]
    ) -> List[Tuple[int, float]]:
        """Ensure variety in recommendations."""
        # TODO: Implement category diversity logic
        return scored_interventions

    def save_state(self) -> Dict:
        """Serialize model state for database storage."""
        return {
            'alpha': self.alpha.tolist(),
            'beta_param': self.beta_param.tolist(),
            'weights': self.weights.tolist(),
            'num_interventions': self.num_interventions,
            'context_dim': self.context_dim
        }

    @classmethod
    def load_state(cls, state: Dict) -> 'ContextualThompsonSampling':
        """Load model from saved state."""
        model = cls(state['num_interventions'], state['context_dim'])
        model.alpha = np.array(state['alpha'])
        model.beta_param = np.array(state['beta_param'])
        model.weights = np.array(state['weights'])
        return model


# Context feature engineering
def build_user_context(
    current_emotion: str,
    energy_level: int,
    time_of_day: str,
    recent_effectiveness: List[float],
    user_preferences: Dict
) -> np.ndarray:
    """
    Build context vector for recommendation engine.
    """
    context = []

    # One-hot encode emotion (12 emotions)
    emotion_idx = EMOTION_LABELS.index(current_emotion)
    emotion_vec = [0] * 12
    emotion_vec[emotion_idx] = 1
    context.extend(emotion_vec)

    # Energy level (normalized)
    context.append(energy_level / 10.0)

    # Time of day (one-hot: morning, afternoon, evening, night)
    time_vec = [0, 0, 0, 0]
    time_map = {'morning': 0, 'afternoon': 1, 'evening': 2, 'night': 3}
    time_vec[time_map[time_of_day]] = 1
    context.extend(time_vec)

    # Recent effectiveness (average of last 5)
    avg_effectiveness = np.mean(recent_effectiveness) if recent_effectiveness else 0.5
    context.append(avg_effectiveness)

    # User preferences (ADHD, ASD flags)
    context.append(1.0 if user_preferences.get('has_adhd') else 0.0)
    context.append(1.0 if user_preferences.get('has_autism_spectrum') else 0.0)

    return np.array(context, dtype=np.float32)
```

### 5.3 Crisis Detection Pipeline

```python
# models/crisis_detector.py

import re
from typing import Dict, List, Tuple
from transformers import pipeline

class CrisisDetector:
    """
    Multi-stage crisis detection system.
    """

    def __init__(self):
        # Stage 1: Keyword flagging (fast)
        self.crisis_keywords = self._load_crisis_keywords()

        # Stage 2: Sentiment intensity model
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="nlptown/bert-base-multilingual-uncased-sentiment"
        )

        # Stage 3: Suicidal ideation classifier (custom trained)
        self.si_classifier = self._load_si_classifier()

        # Thresholds
        self.keyword_alert_threshold = 2
        self.sentiment_threshold = -0.7
        self.si_threshold = 0.6

    def _load_crisis_keywords(self) -> Dict[str, float]:
        """Crisis keywords with risk weights."""
        return {
            # High risk
            'suicide': 1.0, 'kill myself': 1.0, 'end it all': 1.0,
            'want to die': 1.0, 'better off dead': 1.0,
            'no reason to live': 0.9, 'can\'t go on': 0.8,

            # Moderate risk
            'self harm': 0.7, 'hurt myself': 0.7, 'cutting': 0.6,
            'hopeless': 0.5, 'worthless': 0.5, 'burden': 0.5,

            # Temporal markers (increase risk when combined)
            'tonight': 0.3, 'soon': 0.3, 'before': 0.3,
            'goodbye': 0.4, 'final': 0.3
        }

    def _load_si_classifier(self):
        """Load fine-tuned suicidal ideation model."""
        # This would be a custom-trained model
        return None  # Placeholder

    def analyze(self, text: str) -> Dict:
        """
        Run full crisis detection pipeline.

        Returns:
            {
                'risk_score': 0.0-1.0,
                'risk_level': 'low'|'moderate'|'high'|'critical',
                'keywords_found': [...],
                'requires_immediate_action': bool,
                'recommended_response': str
            }
        """
        results = {
            'risk_score': 0.0,
            'risk_level': 'low',
            'keywords_found': [],
            'requires_immediate_action': False,
            'recommended_response': 'continue_normal'
        }

        # Stage 1: Fast keyword scan
        keyword_score, keywords = self._keyword_scan(text)
        results['keywords_found'] = keywords

        if keyword_score > 0.8:
            results['risk_score'] = keyword_score
            results['risk_level'] = 'critical'
            results['requires_immediate_action'] = True
            results['recommended_response'] = 'show_crisis_resources'
            return results

        # Stage 2: Sentiment analysis
        sentiment_score = self._sentiment_analysis(text)

        # Stage 3: SI classification (if available)
        si_score = 0.0
        if self.si_classifier:
            si_score = self._si_classification(text)

        # Combine scores
        combined_score = (
            0.4 * keyword_score +
            0.3 * max(0, -sentiment_score) +
            0.3 * si_score
        )

        results['risk_score'] = combined_score

        # Determine risk level
        if combined_score > 0.7:
            results['risk_level'] = 'critical'
            results['requires_immediate_action'] = True
            results['recommended_response'] = 'show_crisis_resources'
        elif combined_score > 0.5:
            results['risk_level'] = 'high'
            results['requires_immediate_action'] = True
            results['recommended_response'] = 'show_crisis_resources'
        elif combined_score > 0.3:
            results['risk_level'] = 'moderate'
            results['recommended_response'] = 'offer_safety_check'
        else:
            results['risk_level'] = 'low'
            results['recommended_response'] = 'continue_normal'

        return results

    def _keyword_scan(self, text: str) -> Tuple[float, List[str]]:
        """Fast keyword detection."""
        text_lower = text.lower()
        found_keywords = []
        total_score = 0.0

        for keyword, weight in self.crisis_keywords.items():
            if keyword in text_lower:
                found_keywords.append(keyword)
                total_score += weight

        # Normalize
        max_possible = sum(self.crisis_keywords.values())
        normalized_score = min(total_score / max_possible, 1.0)

        return normalized_score, found_keywords

    def _sentiment_analysis(self, text: str) -> float:
        """
        Analyze sentiment intensity.
        Returns -1 (very negative) to 1 (very positive)
        """
        result = self.sentiment_pipeline(text[:512])[0]
        # Convert star rating to sentiment score
        # 1-star = -1, 5-star = 1
        label = result['label']
        if '1' in label:
            return -1.0
        elif '2' in label:
            return -0.5
        elif '3' in label:
            return 0.0
        elif '4' in label:
            return 0.5
        else:
            return 1.0

    def _si_classification(self, text: str) -> float:
        """
        Custom suicidal ideation classification.
        Returns probability 0-1.
        """
        if not self.si_classifier:
            return 0.0
        # Placeholder for actual model inference
        return 0.0
```

---

## 6. SECURITY IMPLEMENTATION

### 6.1 Authentication Flow

```javascript
// services/auth/jwt.service.js

const jwt = require('jsonwebtoken');
const crypto = require('crypto');

class JWTService {
  constructor() {
    this.accessTokenSecret = process.env.JWT_ACCESS_SECRET;
    this.refreshTokenSecret = process.env.JWT_REFRESH_SECRET;
    this.accessTokenExpiry = '15m';
    this.refreshTokenExpiry = '7d';
  }

  generateAccessToken(userId, permissions = []) {
    return jwt.sign(
      {
        sub: userId,
        permissions,
        type: 'access',
        jti: crypto.randomUUID(),
      },
      this.accessTokenSecret,
      { expiresIn: this.accessTokenExpiry }
    );
  }

  generateRefreshToken(userId) {
    return jwt.sign(
      {
        sub: userId,
        type: 'refresh',
        jti: crypto.randomUUID(),
      },
      this.refreshTokenSecret,
      { expiresIn: this.refreshTokenExpiry }
    );
  }

  verifyAccessToken(token) {
    try {
      return jwt.verify(token, this.accessTokenSecret);
    } catch (error) {
      throw new AuthenticationError('Invalid or expired token');
    }
  }

  verifyRefreshToken(token) {
    try {
      return jwt.verify(token, this.refreshTokenSecret);
    } catch (error) {
      throw new AuthenticationError('Invalid refresh token');
    }
  }
}

// Middleware
const authMiddleware = async (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'No token provided' });
  }

  const token = authHeader.split(' ')[1];

  try {
    const decoded = jwtService.verifyAccessToken(token);
    req.userId = decoded.sub;
    req.permissions = decoded.permissions;

    // Check if token is blacklisted (for logout)
    const isBlacklisted = await redis.get(`blacklist:${token}`);
    if (isBlacklisted) {
      return res.status(401).json({ error: 'Token has been revoked' });
    }

    next();
  } catch (error) {
    return res.status(401).json({ error: error.message });
  }
};
```

### 6.2 Data Encryption

```javascript
// services/encryption.service.js

const crypto = require('crypto');

class EncryptionService {
  constructor() {
    this.algorithm = 'aes-256-gcm';
    this.keyLength = 32; // 256 bits
    this.ivLength = 16;
    this.tagLength = 16;
    this.masterKey = Buffer.from(process.env.ENCRYPTION_KEY, 'hex');
  }

  /**
   * Encrypt sensitive data (journal entries, etc.)
   */
  encrypt(plaintext) {
    const iv = crypto.randomBytes(this.ivLength);
    const cipher = crypto.createCipheriv(this.algorithm, this.masterKey, iv);

    let encrypted = cipher.update(plaintext, 'utf8', 'hex');
    encrypted += cipher.final('hex');

    const tag = cipher.getAuthTag();

    // Combine IV + Tag + Encrypted data
    return {
      iv: iv.toString('hex'),
      tag: tag.toString('hex'),
      data: encrypted,
    };
  }

  /**
   * Decrypt sensitive data
   */
  decrypt(encryptedObj) {
    const iv = Buffer.from(encryptedObj.iv, 'hex');
    const tag = Buffer.from(encryptedObj.tag, 'hex');
    const encryptedData = encryptedObj.data;

    const decipher = crypto.createDecipheriv(
      this.algorithm,
      this.masterKey,
      iv
    );
    decipher.setAuthTag(tag);

    let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
  }

  /**
   * Hash sensitive data for searching (e.g., email)
   */
  hash(data) {
    return crypto.createHmac('sha256', this.masterKey).update(data).digest('hex');
  }
}

module.exports = new EncryptionService();
```

### 6.3 HIPAA Compliance Checklist

```markdown
## HIPAA Technical Safeguards Implementation

### Access Controls
- [ ] Unique user identification (UUID-based)
- [ ] Emergency access procedure documented
- [ ] Automatic logoff (15 min inactivity)
- [ ] Encryption/decryption mechanisms (AES-256-GCM)

### Audit Controls
- [ ] Hardware, software, procedural mechanisms to record activity
- [ ] Detailed audit logs with timestamps
- [ ] User ID tracking for all data access
- [ ] Log retention policy (6 years minimum)

### Integrity Controls
- [ ] Data validation on input
- [ ] Checksums for stored data
- [ ] Version control for all changes
- [ ] Regular integrity verification

### Transmission Security
- [ ] TLS 1.3 for all data in transit
- [ ] Certificate pinning for mobile apps
- [ ] End-to-end encryption for sensitive data
- [ ] VPN for internal communications

### Person/Entity Authentication
- [ ] Multi-factor authentication available
- [ ] Password complexity requirements (12+ chars)
- [ ] Failed login attempt limits (5 attempts)
- [ ] Session management and timeout
```

---

## 7. DEPLOYMENT ARCHITECTURE

### 7.1 Kubernetes Deployment

```yaml
# kubernetes/firefly-core-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: firefly-core-api
  labels:
    app: firefly-core
spec:
  replicas: 3
  selector:
    matchLabels:
      app: firefly-core
  template:
    metadata:
      labels:
        app: firefly-core
    spec:
      containers:
        - name: firefly-core
          image: firefly/core-api:latest
          ports:
            - containerPort: 3002
          env:
            - name: NODE_ENV
              value: 'production'
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: firefly-secrets
                  key: database-url
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: firefly-secrets
                  key: redis-url
          resources:
            requests:
              memory: '256Mi'
              cpu: '250m'
            limits:
              memory: '512Mi'
              cpu: '500m'
          livenessProbe:
            httpGet:
              path: /health
              port: 3002
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /ready
              port: 3002
            initialDelaySeconds: 5
            periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: firefly-core-service
spec:
  selector:
    app: firefly-core
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3002
  type: ClusterIP

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: firefly-core-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: firefly-core-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### 7.2 CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml

name: Deploy Firefly

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linting
        run: npm run lint

      - name: Run tests
        run: npm run test:coverage

      - name: Security audit
        run: npm audit --audit-level=high

  build-and-deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v1

      - name: Build and push Docker image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: firefly-core
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

      - name: Deploy to Kubernetes
        run: |
          aws eks update-kubeconfig --name firefly-cluster
          kubectl set image deployment/firefly-core-api firefly-core=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
          kubectl rollout status deployment/firefly-core-api
```

---

## 8. MONITORING & OBSERVABILITY

### 8.1 Metrics Stack

```yaml
# Prometheus + Grafana setup

# prometheus-config.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'firefly-services'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app]
        regex: firefly-.*
        action: keep

# Key metrics to track
# - http_requests_total
# - http_request_duration_seconds
# - checkin_created_total
# - intervention_completed_total
# - crisis_detected_total
# - ml_model_inference_duration_seconds
# - database_query_duration_seconds
# - user_session_duration_seconds
```

### 8.2 Error Tracking (Sentry)

```javascript
// sentry.config.js
const Sentry = require('@sentry/node');

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: process.env.APP_VERSION,

  // Performance monitoring
  tracesSampleRate: 0.1,

  // Filter sensitive data
  beforeSend(event) {
    // Remove any PII from error reports
    if (event.user) {
      delete event.user.email;
      delete event.user.ip_address;
    }

    // Scrub sensitive fields
    if (event.request && event.request.data) {
      delete event.request.data.password;
      delete event.request.data.journal_text;
    }

    return event;
  },
});
```

---

## 9. COST ESTIMATION

### 9.1 Infrastructure Costs (AWS, 10K Users)

| Service                 | Monthly Cost (USD) |
| ----------------------- | ------------------ |
| EKS Cluster             | $146               |
| EC2 Instances (3x m5)   | $250               |
| RDS PostgreSQL (db.r5)  | $200               |
| ElastiCache Redis       | $120               |
| S3 Storage              | $50                |
| CloudFront CDN          | $100               |
| Data Transfer           | $150               |
| ML Inference (SageMaker)| $300               |
| Monitoring (CloudWatch) | $100               |
| **Total**               | **~$1,416/month**  |

### 9.2 Third-Party Services

| Service         | Monthly Cost |
| --------------- | ------------ |
| Sentry          | $29          |
| Datadog         | $150         |
| SendGrid (email)| $35          |
| Twilio (SMS)    | $100         |
| **Total**       | **~$314**    |

**Total Infrastructure: ~$1,730/month for 10K users**

---

## 10. NEXT STEPS

1. **Week 1-2:** Set up development environment
   - Initialize Git repository
   - Configure Docker development environment
   - Set up PostgreSQL and Redis locally
   - Create initial database migrations

2. **Week 3-4:** Core service development
   - User registration and authentication
   - Basic check-in API
   - Intervention library CRUD

3. **Week 5-6:** ML pipeline setup
   - Train initial emotion classifier
   - Implement basic recommendation engine
   - Set up model serving infrastructure

4. **Week 7-8:** Frontend development
   - React web app scaffolding
   - Onboarding flow
   - Check-in interface

5. **Week 9-10:** Integration and testing
   - End-to-end testing
   - Security audit
   - Performance optimization

6. **Week 11-12:** Beta launch preparation
   - Deploy to staging environment
   - Beta user recruitment
   - Documentation completion

---

**This technical architecture provides a solid foundation for building Firefly with scalability, security, and clinical effectiveness at its core.**
