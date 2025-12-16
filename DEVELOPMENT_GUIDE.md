# Firefly Development Quick Start Guide
## Getting Your Development Environment Ready

---

## Overview

This guide walks you through setting up the Firefly development environment from scratch. By the end, you'll have:

- Database infrastructure (PostgreSQL + Redis)
- Backend API services (Node.js + Python ML)
- Frontend web application (React)
- Basic intervention library seeded
- ML model placeholders ready for training

---

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| Node.js | 18.x LTS | Frontend + Backend API |
| npm/yarn | Latest | Package management |
| Python | 3.10+ | ML/AI services |
| PostgreSQL | 15+ | Primary database |
| Redis | 7+ | Caching, sessions, queues |
| Docker | Latest | Container orchestration |
| Git | Latest | Version control |

### Recommended Tools

- VS Code with extensions: ESLint, Prettier, Python, PostgreSQL
- Postman or Insomnia (API testing)
- pgAdmin or DBeaver (database management)
- Redis Insight (Redis monitoring)

---

## Project Structure (Recommended)

```
firefly/
├── docs/                          # Documentation (you are here)
│   ├── README.md
│   ├── FIREFLY_ENHANCED_SPECIFICATION.md
│   ├── TECHNICAL_ARCHITECTURE.md
│   ├── USER_JOURNEYS.md
│   ├── RESEARCH_FINDINGS.md
│   └── DEVELOPMENT_GUIDE.md
│
├── frontend/                      # React Web Application
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/           # Shared UI components
│   │   │   ├── checkin/          # Mood check-in flow
│   │   │   ├── interventions/    # Intervention cards/timers
│   │   │   ├── insights/         # Weekly summaries, charts
│   │   │   ├── onboarding/       # First-time user flow
│   │   │   └── garden/           # Firefly garden gamification
│   │   ├── hooks/                # Custom React hooks
│   │   ├── services/             # API client services
│   │   ├── store/                # State management (Redux/Zustand)
│   │   ├── styles/               # Global styles, themes
│   │   ├── utils/                # Helper functions
│   │   └── App.tsx
│   ├── package.json
│   └── tsconfig.json
│
├── backend/                       # Node.js API Services
│   ├── src/
│   │   ├── config/               # Environment config
│   │   ├── controllers/          # Route handlers
│   │   ├── middleware/           # Auth, validation, logging
│   │   ├── models/               # Database models (Prisma)
│   │   ├── services/             # Business logic
│   │   ├── routes/               # API route definitions
│   │   ├── utils/                # Helper utilities
│   │   └── app.ts                # Express app setup
│   ├── prisma/
│   │   ├── schema.prisma         # Database schema
│   │   ├── migrations/           # Migration files
│   │   └── seed.ts               # Seed data
│   ├── tests/                    # Jest test files
│   ├── package.json
│   └── tsconfig.json
│
├── ml-service/                    # Python ML/AI Services
│   ├── models/
│   │   ├── emotion_classifier.py
│   │   ├── recommendation_engine.py
│   │   ├── crisis_detector.py
│   │   └── model_weights/        # Trained model files
│   ├── api/
│   │   ├── main.py               # FastAPI app
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── training/
│   │   ├── train_emotion.py
│   │   ├── train_crisis.py
│   │   └── datasets/
│   ├── requirements.txt
│   └── pytest.ini
│
├── mobile/                        # React Native (Phase 3)
│   ├── ios/
│   ├── android/
│   └── src/
│
├── infrastructure/                # DevOps & Deployment
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   ├── Dockerfile.backend
│   │   ├── Dockerfile.ml
│   │   └── Dockerfile.frontend
│   ├── kubernetes/
│   │   ├── deployments/
│   │   ├── services/
│   │   └── configmaps/
│   └── terraform/
│       └── main.tf
│
├── scripts/                       # Utility scripts
│   ├── setup.sh
│   ├── seed-interventions.js
│   └── generate-migrations.sh
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── deploy.yml
│   │   └── security-scan.yml
│   └── ISSUE_TEMPLATE/
│
├── .env.example
├── .gitignore
├── package.json                   # Root workspace config
└── README.md
```

---

## Step-by-Step Setup

### Step 1: Clone and Initialize

```bash
# Create project directory
mkdir firefly && cd firefly

# Initialize git
git init

# Create initial structure
mkdir -p frontend backend ml-service infrastructure scripts docs

# Copy documentation files (already created)
# README.md, FIREFLY_ENHANCED_SPECIFICATION.md, etc.
```

### Step 2: Set Up Environment Variables

Create `.env` file in root:

```env
# Database
DATABASE_URL=postgresql://firefly_user:secure_password@localhost:5432/firefly_db
REDIS_URL=redis://localhost:6379

# Authentication
JWT_ACCESS_SECRET=your-super-secret-access-key-at-least-32-chars
JWT_REFRESH_SECRET=your-super-secret-refresh-key-at-least-32-chars
ENCRYPTION_KEY=your-256-bit-encryption-key-in-hex

# API Configuration
NODE_ENV=development
API_PORT=3002
ML_SERVICE_URL=http://localhost:5001

# Frontend
REACT_APP_API_URL=http://localhost:3002/api/v1

# ML Service
ML_SERVICE_PORT=5001
MODEL_PATH=./ml-service/models/model_weights

# External Services (configure later)
SENTRY_DSN=
SENDGRID_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=

# Feature Flags
ENABLE_CRISIS_DETECTION=true
ENABLE_ML_RECOMMENDATIONS=true
ENABLE_WEARABLE_INTEGRATION=false
```

### Step 3: Database Setup

#### Option A: Docker (Recommended)

Create `infrastructure/docker/docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: firefly-postgres
    environment:
      POSTGRES_USER: firefly_user
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: firefly_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U firefly_user -d firefly_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: firefly-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  # Optional: Elasticsearch for search
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
    container_name: firefly-elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:
```

Start services:

```bash
cd infrastructure/docker
docker-compose up -d

# Verify running
docker-compose ps
```

#### Option B: Local Installation

Install PostgreSQL and Redis natively on your system.

### Step 4: Backend Setup (Node.js)

```bash
cd backend

# Initialize Node project
npm init -y

# Install core dependencies
npm install express typescript ts-node @types/node @types/express
npm install prisma @prisma/client
npm install jsonwebtoken bcrypt uuid
npm install zod dotenv cors helmet
npm install bull ioredis
npm install @sentry/node

# Install dev dependencies
npm install -D nodemon jest @types/jest ts-jest
npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install -D prettier

# Initialize TypeScript
npx tsc --init

# Initialize Prisma
npx prisma init
```

Create `backend/package.json` scripts:

```json
{
  "scripts": {
    "dev": "nodemon src/app.ts",
    "build": "tsc",
    "start": "node dist/app.js",
    "test": "jest",
    "lint": "eslint src/**/*.ts",
    "db:migrate": "prisma migrate dev",
    "db:push": "prisma db push",
    "db:seed": "ts-node prisma/seed.ts",
    "db:studio": "prisma studio"
  }
}
```

### Step 5: Prisma Schema (Database Models)

Create `backend/prisma/schema.prisma`:

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id                String    @id @default(uuid())
  email             String    @unique
  passwordHash      String    @map("password_hash")
  displayName       String?   @map("display_name")
  createdAt         DateTime  @default(now()) @map("created_at")
  updatedAt         DateTime  @updatedAt @map("updated_at")
  lastLogin         DateTime? @map("last_login")
  isActive          Boolean   @default(true) @map("is_active")
  isPremium         Boolean   @default(false) @map("is_premium")
  subscriptionTier  String    @default("free") @map("subscription_tier")

  // Neurodiversity flags
  hasAdhd            Boolean  @default(false) @map("has_adhd")
  hasAutismSpectrum  Boolean  @default(false) @map("has_autism_spectrum")
  hasAnxiety         Boolean  @default(false) @map("has_anxiety")
  hasDepression      Boolean  @default(false) @map("has_depression")

  // Privacy
  dataSharingConsent Boolean @default(false) @map("data_sharing_consent")

  // Relations
  preferences       UserPreferences?
  checkins          MoodCheckin[]
  sessions          InterventionSession[]
  mlModel           UserMLModel?
  achievements      UserAchievement[]
  weeklySummaries   WeeklySummary[]
  crisisEvents      CrisisEvent[]

  @@map("users")
}

model UserPreferences {
  id                   String   @id @default(uuid())
  userId               String   @unique @map("user_id")
  createdAt            DateTime @default(now()) @map("created_at")
  updatedAt            DateTime @updatedAt @map("updated_at")

  // Visual
  theme                String   @default("calm_light")
  fontSize             Int      @default(16) @map("font_size")
  animationSpeed       String   @default("normal") @map("animation_speed")
  reduceMotion         Boolean  @default(false) @map("reduce_motion")

  // Notifications
  morningCheckinEnabled Boolean  @default(true) @map("morning_checkin_enabled")
  morningCheckinTime    String   @default("08:00") @map("morning_checkin_time")
  maxNotificationsPerDay Int     @default(3) @map("max_notifications_per_day")

  // ADHD specific
  timeBlindnessSupport  Boolean @default(false) @map("time_blindness_support")
  taskBreakdownAuto     Boolean @default(false) @map("task_breakdown_auto")

  // ASD specific
  sensoryLoadTracking   Boolean @default(false) @map("sensory_load_tracking")
  routineDeviationAlerts Boolean @default(false) @map("routine_deviation_alerts")

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("user_preferences")
}

model MoodCheckin {
  id               String   @id @default(uuid())
  userId           String   @map("user_id")
  createdAt        DateTime @default(now()) @map("created_at")

  moodScore        Int      @map("mood_score")
  energyLevel      Int      @map("energy_level")
  anxietyLevel     Int?     @map("anxiety_level")
  stressLevel      Int?     @map("stress_level")

  emotionTags      String[] @map("emotion_tags")
  journalText      String?  @map("journal_text")
  contextLocation  String?  @map("context_location")

  // AI analysis
  aiEmotionPrimary    String?   @map("ai_emotion_primary")
  aiConfidenceScore   Float?    @map("ai_confidence_score")
  crisisRiskScore     Float     @default(0) @map("crisis_risk_score")
  crisisFlagged       Boolean   @default(false) @map("crisis_flagged")

  user     User                  @relation(fields: [userId], references: [id], onDelete: Cascade)
  sessions InterventionSession[]

  @@index([userId, createdAt(sort: Desc)])
  @@map("mood_checkins")
}

model Intervention {
  id                  String   @id @default(uuid())
  name                String
  shortDescription    String   @map("short_description")
  detailedInstructions String  @map("detailed_instructions")
  durationSeconds     Int      @map("duration_seconds")
  effortLevel         String   @map("effort_level")
  therapeuticApproach String   @map("therapeutic_approach")

  targetEmotions      String[] @map("target_emotions")
  adhdFriendly        Boolean  @default(true) @map("adhd_friendly")
  asdFriendly         Boolean  @default(true) @map("asd_friendly")

  isActive            Boolean  @default(true) @map("is_active")
  isPremium           Boolean  @default(false) @map("is_premium")

  globalEffectivenessScore Float @default(0.5) @map("global_effectiveness_score")

  sessions InterventionSession[]

  @@map("interventions")
}

model InterventionSession {
  id              String    @id @default(uuid())
  userId          String    @map("user_id")
  interventionId  String    @map("intervention_id")
  checkinId       String?   @map("checkin_id")
  createdAt       DateTime  @default(now()) @map("created_at")

  startedAt       DateTime  @map("started_at")
  completedAt     DateTime? @map("completed_at")
  wasCompleted    Boolean   @default(false) @map("was_completed")

  effectivenessRating Int?  @map("effectiveness_rating")
  feedbackTags    String[]  @map("feedback_tags")

  predictedEffectiveness Float? @map("predicted_effectiveness")
  actualEffectiveness    Float? @map("actual_effectiveness")

  user         User          @relation(fields: [userId], references: [id], onDelete: Cascade)
  intervention Intervention  @relation(fields: [interventionId], references: [id])
  checkin      MoodCheckin?  @relation(fields: [checkinId], references: [id])

  @@index([userId, createdAt(sort: Desc)])
  @@map("intervention_sessions")
}

model UserMLModel {
  id            String   @id @default(uuid())
  userId        String   @unique @map("user_id")
  createdAt     DateTime @default(now()) @map("created_at")
  updatedAt     DateTime @updatedAt @map("updated_at")

  banditModelState          Json @default("{}") @map("bandit_model_state")
  interventionPriorBeliefs  Json @default("{}") @map("intervention_prior_beliefs")
  circadianPatterns         Json @default("{}") @map("circadian_patterns")
  triggerPatterns           Json @default("{}") @map("trigger_patterns")

  totalInteractions Int @default(0) @map("total_interactions")

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("user_ml_models")
}

model UserAchievement {
  id              String   @id @default(uuid())
  userId          String   @map("user_id")
  achievementType String   @map("achievement_type")
  achievedAt      DateTime @default(now()) @map("achieved_at")
  metadata        Json     @default("{}")

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([userId, achievementType])
  @@map("user_achievements")
}

model WeeklySummary {
  id               String   @id @default(uuid())
  userId           String   @map("user_id")
  weekStartDate    DateTime @map("week_start_date")
  createdAt        DateTime @default(now()) @map("created_at")

  totalCheckins    Int      @default(0) @map("total_checkins")
  averageMoodScore Float?   @map("average_mood_score")
  moodTrend        String?  @map("mood_trend")

  mostCommonEmotions          String[] @map("most_common_emotions")
  mostEffectiveInterventions  String[] @map("most_effective_interventions")
  summaryNarrative            String?  @map("summary_narrative")

  streakLength              Int    @default(0) @map("streak_length")
  interventionsCompleted    Int    @default(0) @map("interventions_completed")

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([userId, weekStartDate])
  @@map("weekly_summaries")
}

model CrisisEvent {
  id              String   @id @default(uuid())
  userId          String   @map("user_id")
  createdAt       DateTime @default(now()) @map("created_at")

  triggerSource   String   @map("trigger_source")
  riskScore       Float    @map("risk_score")
  riskLevel       String   @map("risk_level")

  immediateResponseShown Boolean @default(true) @map("immediate_response_shown")
  hotlineInfoDisplayed   Boolean @default(false) @map("hotline_info_displayed")

  resolved        Boolean  @default(false)
  resolvedAt      DateTime? @map("resolved_at")

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@index([userId, createdAt(sort: Desc)])
  @@map("crisis_events")
}

model AuditLog {
  id             String   @id @default(uuid())
  timestamp      DateTime @default(now())
  userId         String?  @map("user_id")
  actionType     String   @map("action_type")
  resourceType   String?  @map("resource_type")
  resourceId     String?  @map("resource_id")
  requestDetails Json?    @map("request_details")

  @@index([userId, timestamp(sort: Desc)])
  @@map("audit_log")
}
```

Run migration:

```bash
npx prisma migrate dev --name init
npx prisma generate
```

### Step 6: Basic Express API

Create `backend/src/app.ts`:

```typescript
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import { PrismaClient } from '@prisma/client';

dotenv.config({ path: '../.env' });

const app = express();
const prisma = new PrismaClient();

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Basic routes placeholder
app.get('/api/v1/interventions', async (req, res) => {
  try {
    const interventions = await prisma.intervention.findMany({
      where: { isActive: true },
      take: 20,
    });
    res.json(interventions);
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

const PORT = process.env.API_PORT || 3002;

app.listen(PORT, () => {
  console.log(`Firefly API running on port ${PORT}`);
});

export default app;
```

### Step 7: Frontend Setup (React)

```bash
cd frontend

# Create React app with TypeScript
npx create-react-app . --template typescript

# Install additional dependencies
npm install @tanstack/react-query axios
npm install zustand  # State management
npm install framer-motion  # Animations
npm install react-router-dom
npm install tailwindcss postcss autoprefixer
npm install @headlessui/react @heroicons/react
npm install chart.js react-chartjs-2  # For mood charts
npm install date-fns  # Date utilities

# Initialize Tailwind
npx tailwindcss init -p
```

Configure Tailwind (`tailwind.config.js`):

```javascript
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'firefly-primary': '#2D7D90',
        'firefly-secondary': '#6B8E23',
        'firefly-accent': '#FFD93D',
        'firefly-calm': '#F5F3F0',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        dyslexic: ['OpenDyslexic', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
```

### Step 8: ML Service Setup (Python)

```bash
cd ml-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn
pip install torch transformers
pip install scikit-learn numpy pandas
pip install pydantic
pip install python-dotenv
```

Create `ml-service/requirements.txt`:

```
fastapi==0.104.1
uvicorn==0.24.0
torch==2.1.1
transformers==4.35.2
scikit-learn==1.3.2
numpy==1.26.2
pandas==2.1.3
pydantic==2.5.2
python-dotenv==1.0.0
```

Create `ml-service/api/main.py`:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import numpy as np

app = FastAPI(title="Firefly ML Service", version="1.0.0")

class EmotionRequest(BaseModel):
    text: str
    user_id: Optional[str] = None

class EmotionResponse(BaseModel):
    primary_emotion: str
    confidence: float
    all_emotions: dict
    crisis_risk: float

class RecommendationRequest(BaseModel):
    user_id: str
    current_emotion: str
    energy_level: int
    time_available_minutes: int

class InterventionRecommendation(BaseModel):
    intervention_id: str
    predicted_effectiveness: float
    reason: str

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ml-service"}

@app.post("/analyze-emotion", response_model=EmotionResponse)
def analyze_emotion(request: EmotionRequest):
    # Placeholder - will integrate actual model
    return EmotionResponse(
        primary_emotion="calm",
        confidence=0.85,
        all_emotions={
            "calm": 0.85,
            "anxiety": 0.10,
            "sadness": 0.05
        },
        crisis_risk=0.02
    )

@app.post("/recommend", response_model=List[InterventionRecommendation])
def get_recommendations(request: RecommendationRequest):
    # Placeholder - will integrate recommendation engine
    return [
        InterventionRecommendation(
            intervention_id="uuid-1",
            predicted_effectiveness=0.82,
            reason="Based on your patterns, box breathing has worked well for you"
        ),
        InterventionRecommendation(
            intervention_id="uuid-2",
            predicted_effectiveness=0.75,
            reason="Quick physical movement matches your current energy level"
        ),
        InterventionRecommendation(
            intervention_id="uuid-3",
            predicted_effectiveness=0.71,
            reason="Grounding exercise for emotional regulation"
        )
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
```

Run:

```bash
python api/main.py
# or
uvicorn api.main:app --reload --port 5001
```

### Step 9: Seed Initial Data

Create `backend/prisma/seed.ts`:

```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('Seeding intervention library...');

  const interventions = [
    {
      name: 'Box Breathing',
      shortDescription: 'Calm your nervous system with 4-count breathing',
      detailedInstructions: `
        1. Breathe in for 4 counts
        2. Hold for 4 counts
        3. Breathe out for 4 counts
        4. Hold for 4 counts
        5. Repeat 4 times
      `,
      durationSeconds: 120,
      effortLevel: 'low',
      therapeuticApproach: 'Mindfulness',
      targetEmotions: ['anxiety', 'overwhelm', 'stress'],
      adhdFriendly: true,
      asdFriendly: true,
    },
    {
      name: 'TIPP - Temperature',
      shortDescription: 'Use cold to quickly reduce intense emotions',
      detailedInstructions: `
        Hold ice cubes or splash cold water on your face.
        The cold activates your dive reflex, slowing heart rate.
        Do this for 30-60 seconds.
      `,
      durationSeconds: 60,
      effortLevel: 'low',
      therapeuticApproach: 'DBT',
      targetEmotions: ['panic', 'rage', 'intense_anxiety'],
      adhdFriendly: true,
      asdFriendly: true,
    },
    {
      name: '5-4-3-2-1 Grounding',
      shortDescription: 'Use your senses to ground yourself in the present',
      detailedInstructions: `
        Name:
        - 5 things you can see
        - 4 things you can touch
        - 3 things you can hear
        - 2 things you can smell
        - 1 thing you can taste
      `,
      durationSeconds: 180,
      effortLevel: 'low',
      therapeuticApproach: 'CBT',
      targetEmotions: ['dissociation', 'anxiety', 'overwhelm'],
      adhdFriendly: true,
      asdFriendly: true,
    },
    // Add more interventions...
  ];

  for (const intervention of interventions) {
    await prisma.intervention.create({
      data: intervention,
    });
  }

  console.log(`Seeded ${interventions.length} interventions`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
```

Run:

```bash
npx ts-node prisma/seed.ts
```

---

## Development Workflow

### Daily Development Commands

```bash
# Start all services
docker-compose up -d  # Database
npm run dev  # Backend (in backend/)
npm start  # Frontend (in frontend/)
python api/main.py  # ML service (in ml-service/)

# Database operations
npm run db:studio  # Open Prisma Studio (visual DB browser)
npm run db:migrate  # Create new migration

# Testing
npm test  # Run all tests
npm run lint  # Check code style

# Build for production
npm run build
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/mood-checkin

# Make changes, then commit
git add .
git commit -m "feat(checkin): add mood slider component"

# Push and create PR
git push origin feature/mood-checkin
```

Commit message convention:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Formatting
- `refactor:` - Code restructuring
- `test:` - Adding tests
- `chore:` - Maintenance

---

## Next Steps After Setup

1. **Week 1:** Core authentication (JWT, registration, login)
2. **Week 2:** Basic check-in API and database storage
3. **Week 3:** Simple recommendation engine (rule-based first)
4. **Week 4:** Frontend check-in flow UI
5. **Week 5:** ML model training (emotion classifier)
6. **Week 6:** Crisis detection implementation
7. **Week 7:** Weekly summary generation
8. **Week 8:** ADHD/ASD specific features

---

## Helpful Resources

- **Prisma Docs:** https://www.prisma.io/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React Query:** https://tanstack.com/query
- **Tailwind CSS:** https://tailwindcss.com/docs
- **Hugging Face Transformers:** https://huggingface.co/docs/transformers

---

## Common Issues & Solutions

### Database connection failed
```bash
# Check if PostgreSQL is running
docker-compose ps

# Check connection string
psql $DATABASE_URL -c "SELECT 1"
```

### ML service import errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend build failures
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

**You're now ready to start building Firefly!**

Start with the authentication system, then move to check-ins, and progressively add features according to the implementation roadmap.

Good luck, and remember: you're building something that could genuinely change lives.
