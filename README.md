# Firefly
## AI-Powered Adaptive Mental Wellness Platform

<div align="center">

**Empowering neurodivergent minds with personalized, evidence-based mental health support**

[Research Findings](./RESEARCH_FINDINGS.md) | [Product Spec](./FIREFLY_ENHANCED_SPECIFICATION.md) | [Technical Architecture](./TECHNICAL_ARCHITECTURE.md) | [User Journeys](./USER_JOURNEYS.md)

</div>

---

## Vision

Firefly is an AI-powered mental wellness platform that adapts to individual cognitive patterns, emotional states, and sensory preferences. Unlike generic mental health apps, Firefly learns from each user's unique patterns and provides truly personalized micro-interventions—with special focus on supporting neurodivergent users (ADHD, Autism Spectrum).

**Our Mission:** To create the world's most effective, inclusive, and scientifically-grounded digital mental health companion.

---

## Why Firefly?

### The Problem

- **3.9%** - Current app 15-day retention (median)
- **15-20%** - Global population that is neurodivergent
- **81%** - Users with suicidal ideation who pass standard screenings
- **60%** - Users worried about data privacy in mental health apps
- **0** - Comprehensive apps supporting ADHD + Autism + evidence-based interventions

### Our Solution

A **Three-Brain Architecture**:

1. **Emotion Brain** - Detects and understands emotional states using NLP and multi-modal analysis
2. **Action Brain** - Recommends evidence-based micro-interventions (DBT, ACT, CBT, Mindfulness)
3. **Adaptation Brain** - Continuously learns and personalizes through reinforcement learning

---

## Key Features

### Core Platform
- Daily mood check-ins (30 seconds)
- 550+ evidence-based micro-interventions
- AI-powered personalized recommendations
- Real-time crisis detection (NLP-based)
- Weekly insights and progress tracking
- Privacy-first, HIPAA-compliant architecture

### Neurodiversity Support

**For ADHD Users:**
- Time blindness toolkit (visual timers, estimation training)
- AI task decomposition engine
- Executive function assessments
- Variable reward system for dopamine management
- Rejection sensitivity dysphoria support

**For Autism Spectrum Users:**
- Sensory load monitoring dashboard
- Emotion identification scaffolding (alexithymia support)
- Routine management with deviation alerts
- Masking exhaustion tracker
- Meltdown prevention system

### Safety & Ethics
- Multi-layer crisis detection (95%+ recall target)
- Immediate crisis resources (988, Crisis Text Line)
- Transparent AI explanations
- User-controlled data sharing
- No medical diagnoses (supportive role only)

---

## Documentation

| Document | Description |
|----------|-------------|
| [FIREFLY_ENHANCED_SPECIFICATION.md](./FIREFLY_ENHANCED_SPECIFICATION.md) | Complete product specification with features, architecture, implementation roadmap |
| [TECHNICAL_ARCHITECTURE.md](./TECHNICAL_ARCHITECTURE.md) | Database schemas, API specs, ML models, security implementation |
| [USER_JOURNEYS.md](./USER_JOURNEYS.md) | Detailed user flows for onboarding, check-ins, crisis, ADHD/ASD support |
| [RESEARCH_FINDINGS.md](./RESEARCH_FINDINGS.md) | Evidence-based research supporting all product decisions |

---

## Technology Stack

### Frontend
- React.js / React Native (Web + Mobile)
- TypeScript
- Tailwind CSS + Custom Design System
- Framer Motion (neurodiversity-friendly animations)

### Backend
- Node.js with Express (Core API)
- Python with FastAPI (ML Services)
- GraphQL for flexible queries
- WebSocket for real-time features

### Database
- PostgreSQL (primary store)
- Redis (caching, sessions)
- Elasticsearch (search, analytics)
- TimescaleDB (time-series mood data)

### AI/ML
- TensorFlow / PyTorch (emotion models)
- Hugging Face Transformers (NLP)
- Contextual Multi-Armed Bandit (recommendations)
- Custom crisis detection pipeline

### Infrastructure
- AWS / Google Cloud Platform
- Kubernetes orchestration
- CloudFlare (CDN, security)
- Docker containers

---

## Implementation Roadmap

### Phase 1: Foundation (Months 1-3) - "First Light" ✅ COMPLETE
- Core infrastructure setup
- Authentication system (JWT with MFA support)
- Basic mood check-ins (mood, energy, emotions, journal)
- Initial intervention library (100+ techniques seeded)
- Simple recommendation engine (rule-based)
- Crisis detection (keyword + behavioral)
- HIPAA-compliant audit logging
- AES-256 encryption service
- Complete React frontend
- User data export/deletion (GDPR/CCPA)

**See [PHASE1_COMPLETE.md](./PHASE1_COMPLETE.md) for full implementation details.**

### Phase 2: Intelligence (Months 4-6) - "Growing Brighter"
- Advanced AI/ML models
- ADHD executive function tools
- Autism sensory dashboard
- Personalization engine
- Clinical validation initiation

### Phase 3: Engagement (Months 7-9) - "Gathering Swarm"
- Firefly garden gamification
- iOS and Android apps
- Adaptive notifications
- Community features (opt-in)

### Phase 4: Integration (Months 10-12) - "Constellation"
- Wearable device integration
- Professional therapist portal
- Multi-language support
- Enterprise licensing
- Public launch

---

## Success Metrics

| Category | Metric | Target |
|----------|--------|--------|
| **Engagement** | 30-day retention | 45%+ (vs. industry 10%) |
| **Effectiveness** | Mood improvement | 40%+ self-reported |
| **Safety** | Crisis detection recall | 95%+ |
| **User Satisfaction** | NPS Score | 50+ |
| **Technical** | System uptime | 99.9% |

---

## Security & Privacy

- **HIPAA Compliant** - End-to-end encryption, audit trails, BAAs
- **User Control** - Full data ownership, export, deletion rights
- **Transparent AI** - Explainable recommendations
- **No Data Sales** - Ever. Privacy is non-negotiable.
- **SOC 2 Type II** - Certification target

---

## Target Users

**Primary:** College students and young adults (18-25)
- Digital natives with short attention spans
- Open to wellness experimentation
- Academic/transition stress peaks

**Secondary:** Young professionals (25-35)
- Work-life balance struggles
- Quick "rescue" intervention needs
- Career transition stress

**Tertiary:** Neurodivergent users (all ages)
- ADHD: Time blindness, executive dysfunction
- Autism Spectrum: Sensory regulation, emotion identification

---

## Monetization Strategy

### Freemium Model
- **Free Tier:** Basic check-ins, 50 interventions, weekly summaries
- **Premium ($9.99/mo):** Full library (550+), advanced AI, wearables
- **Family Plan ($14.99/mo):** Up to 5 members

### B2B Revenue
- University campus licensing
- Healthcare EHR integration
- Corporate wellness programs
- Research partnerships

### Grant Funding
- NIMH, PCORI, Mental Health foundations
- Neurodiversity advocacy organizations

---

## Getting Started (Development)

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

### Quick Setup (Phase 1 Implemented)

```bash
# One-click startup (Windows)
.\quickstart.bat

# Or manually:

# 1. Start Backend (Terminal 1)
cd backend
.\start.bat
# API runs on http://localhost:8000

# 2. Seed Database (once)
cd backend
.\seed_db.bat
# Seeds 100+ interventions

# 3. Start Frontend (Terminal 2)
cd frontend
npm run dev
# Frontend runs on http://localhost:5173
```

### Access Points
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **API ReDoc:** http://localhost:8000/redoc

### Development Commands

```bash
npm run dev          # Start development servers
npm run test         # Run test suite
npm run lint         # Code linting
npm run build        # Production build
npm run db:migrate   # Run database migrations
npm run db:seed      # Seed initial data
```

---

## Contributing

We're building something that could genuinely change lives. Contributions are welcome in:

- **Clinical Expertise** - Evidence-based intervention review
- **ML/AI Development** - Emotion classification, recommendation engine
- **Frontend Development** - Neurodiversity-friendly UX
- **Backend Development** - Scalable, secure architecture
- **Research** - Clinical validation studies
- **Design** - Accessible, calming interfaces

### Code Standards
- TypeScript for type safety
- ESLint + Prettier for consistency
- Jest for testing (80%+ coverage target)
- Conventional commits

---

## Research Foundation

This project is built on extensive research from:
- 50+ peer-reviewed studies (2020-2025)
- Meta-analyses on digital mental health interventions
- ADHD and Autism Spectrum digital therapy research
- AI/ML applications in mental health detection
- Gamification effectiveness studies
- HIPAA compliance requirements

See [RESEARCH_FINDINGS.md](./RESEARCH_FINDINGS.md) for complete analysis.

---

## Ethical Principles

1. **Do No Harm** - Safety above engagement
2. **Respect Autonomy** - User controls their experience
3. **Promote Inclusivity** - Neurodiversity-affirming
4. **Maintain Transparency** - Clear AI limitations
5. **Protect Privacy** - No compromises

---

## Disclaimer

Firefly is a **wellness support tool**, not a replacement for professional mental health treatment. It does not:
- Provide medical diagnoses
- Replace therapy or medication
- Claim to cure mental health conditions
- Guarantee specific outcomes

Always consult healthcare professionals for serious mental health concerns.

---

## License

[To be determined - likely MIT or Apache 2.0 for open-source components]

---

## Contact & Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/firefly/issues)
- **Email:** support@firefly.app (placeholder)
- **Documentation:** [Full Docs](./docs/)

---

## Acknowledgments

Built with gratitude for:
- The mental health research community
- Neurodiversity advocates and educators
- Open-source software contributors
- Early beta testers and feedback providers
- Clinical advisors (to be assembled)

---

<div align="center">

**Firefly: Lighting the way to personalized mental wellness**

*Because every mind deserves support that understands its unique patterns*

</div>
