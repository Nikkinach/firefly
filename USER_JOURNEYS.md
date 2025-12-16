# Firefly User Journey Maps
## Detailed User Flows and Interaction Patterns

---

## 1. FIRST-TIME USER ONBOARDING JOURNEY

### Journey Map: Sarah, 22, College Student with ADHD

```
┌─────────────────────────────────────────────────────────────────┐
│                    SARAH'S ONBOARDING JOURNEY                   │
└─────────────────────────────────────────────────────────────────┘

TIME: 0-10 minutes (critical first impression window)

┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│   App   │     │ Welcome │     │  Quick  │     │  First  │
│ Download│ ──▶ │  Screen │ ──▶ │  Setup  │ ──▶ │ Check-in│
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │
     │               │               │               │
     ▼               ▼               ▼               ▼
 "Let me try"   "Oh, this is    "It's asking   "I can do
  this mental    different—      about MY        this in
  health app"    friendly, not   brain type!"    30 seconds!"
                 clinical"
```

### Step-by-Step Flow

#### Screen 1: Welcome (5 seconds)
```
┌────────────────────────────┐
│                            │
│      ✨ 🔥 ✨              │
│                            │
│     Welcome to Firefly     │
│                            │
│   Your personal companion  │
│   for mental wellness      │
│                            │
│  "No judgment, just        │
│   gentle support"          │
│                            │
│    [Get Started] ──────▶   │
│                            │
│   Already have account?    │
│        Sign in             │
│                            │
└────────────────────────────┘
```
**Emotion Goal:** Warmth, safety, non-clinical
**UX Principle:** Minimal text, clear CTA

#### Screen 2: Cognitive Style Selection (15 seconds)
```
┌────────────────────────────┐
│                            │
│   How does your brain      │
│   work best?               │
│                            │
│   [🎨 I'm visual]          │
│   Pictures speak louder    │
│                            │
│   [📝 I like text]         │
│   Words help me think      │
│                            │
│   [🎵 I'm an audio         │
│       learner]             │
│   I prefer listening       │
│                            │
│   [🔀 Mix it up]           │
│   I like variety           │
│                            │
│   This helps us customize  │
│   your experience          │
│                            │
└────────────────────────────┘
```
**Sarah's Choice:** "I'm visual" (ADHD preference)
**Backend Action:** Set `visual_primary = true`

#### Screen 3: Neurodiversity Acknowledgment (10 seconds)
```
┌────────────────────────────┐
│                            │
│   Do any of these          │
│   resonate with you?       │
│                            │
│   (Select all that apply)  │
│                            │
│   [✓] ADHD                 │
│   [ ] Autism/Asperger's    │
│   [ ] Anxiety              │
│   [ ] Depression           │
│   [ ] I'd rather not say   │
│   [ ] None of the above    │
│                            │
│   💡 This helps us         │
│   provide tools that       │
│   actually work for YOU    │
│                            │
│          [Next] ──────▶    │
│                            │
└────────────────────────────┘
```
**Sarah's Selection:** ADHD + Anxiety
**Backend Action:** Enable ADHD toolkit, anxiety interventions

#### Screen 4: Sensory Preferences (20 seconds)
```
┌────────────────────────────┐
│                            │
│   Customize your           │
│   environment              │
│                            │
│   Interface Brightness:    │
│   [🌙 ═════●═══ ☀️]       │
│          Soft              │
│                            │
│   Animations:              │
│   [● Calm] [○ Moderate]    │
│                            │
│   Sounds:                  │
│   [✓] Gentle chimes        │
│   [ ] Nature sounds        │
│   [ ] Silent mode          │
│                            │
│   Colors:                  │
│   🟢 Calming  ✓            │
│   🟡 Neutral               │
│   🔵 Focus-enhancing       │
│                            │
│        [Continue] ──────▶  │
│                            │
└────────────────────────────┘
```
**Sarah's Preferences:** Soft light, calm animations, gentle sounds
**Impact:** Reduces sensory overload for ADHD

#### Screen 5: First Mood Check-in (30 seconds)
```
┌────────────────────────────┐
│                            │
│   Right now, I feel...     │
│                            │
│   😫 😟 😐 🙂 😊            │
│              ▲              │
│         [Selected]          │
│                            │
│   My energy is:            │
│   🔋 [════●════]           │
│         Medium              │
│                            │
│   What's present?          │
│   [📚 School stress]  ✓    │
│   [💭 Anxious thoughts]    │
│   [🏃 Restless]  ✓         │
│   [😴 Tired]               │
│   [💪 Motivated]           │
│                            │
│   [Complete Check-in]      │
│                            │
└────────────────────────────┘
```
**Sarah's State:** Neutral mood, medium energy, school stress + restless
**AI Analysis:** ADHD restlessness + academic anxiety detected

#### Screen 6: First Recommendation (5 seconds to read)
```
┌────────────────────────────┐
│                            │
│   Here's what might help:  │
│                            │
│   ┌──────────────────┐     │
│   │ 🏃 Quick Movement │     │
│   │    2 minutes      │     │
│   │                   │     │
│   │ Shake out your   │     │
│   │ restless energy  │     │
│   │                   │     │
│   │ Why: You said    │     │
│   │ you're feeling   │     │
│   │ restless         │     │
│   │                   │     │
│   │   [Try This] ▶   │     │
│   └──────────────────┘     │
│                            │
│   [Skip for now]           │
│                            │
│   2 more suggestions       │
│   available ▼              │
│                            │
└────────────────────────────┘
```
**Recommendation Logic:**
- ADHD + Restless → Physical intervention
- Short duration (ADHD attention span)
- Visual progress indicator

#### Screen 7: Intervention Completion
```
┌────────────────────────────┐
│                            │
│   ✨ Great job! ✨         │
│                            │
│   You completed your first │
│   micro-action!            │
│                            │
│   How did that feel?       │
│                            │
│   😕 Not helpful           │
│   🤷 Neutral               │
│   😊 Somewhat helpful  ✓   │
│   🌟 Really helpful        │
│                            │
│   ┌──────────────────┐     │
│   │ 🔥 First Firefly │     │
│   │   Unlocked!      │     │
│   └──────────────────┘     │
│                            │
│   Your firefly garden      │
│   has begun to glow...     │
│                            │
│      [See My Garden]       │
│                            │
└────────────────────────────┘
```
**Feedback Loop:** "Somewhat helpful" updates ML model
**Gamification:** First achievement unlocked (instant gratification)

#### Screen 8: Notification Setup
```
┌────────────────────────────┐
│                            │
│   Stay on track with       │
│   gentle reminders         │
│                            │
│   Morning check-in:        │
│   [✓] 8:30 AM              │
│   (Adjust based on your    │
│    class schedule)         │
│                            │
│   Evening reflection:      │
│   [✓] 9:00 PM              │
│                            │
│   Max notifications/day:   │
│   [ 3 ▾ ]                  │
│                            │
│   💡 We'll learn your      │
│   best times over the      │
│   next week                │
│                            │
│        [Finish Setup]      │
│                            │
│   You can change these     │
│   anytime in settings      │
│                            │
└────────────────────────────┘
```
**Personalization:** ADHD needs external reminders
**Respect:** User controls notification frequency

---

## 2. DAILY CHECK-IN JOURNEY

### Journey Map: Marcus, 28, Software Developer with Anxiety

```
MORNING ROUTINE (2-3 minutes)

07:45 ─────────────────────────────────────────────────▶ 07:48
  │                                                        │
  ▼                                                        ▼
📱 Notification        Quick tap check-in           See top 3
  appears              Mood + Energy                recommendations
                            │
                            ▼
                    Choose morning breathing
                            │
                            ▼
                      Complete in 60 sec
                            │
                            ▼
                      Rate effectiveness
                            │
                            ▼
                     Start day feeling
                        more centered
```

### Detailed Flow

#### Notification (Morning, 7:45 AM)
```
┌────────────────────────────────────────┐
│ 🔥 Firefly                    now      │
│                                        │
│ Good morning! Quick check-in?         │
│ (Takes 30 seconds)                     │
│                                        │
│ [Open App]          [Snooze 15 min]   │
└────────────────────────────────────────┘
```

#### Quick Mode Check-in
```
┌────────────────────────────┐
│      Morning Check-in      │
│                            │
│   Mood:                    │
│   😫 😟 😐 🙂 😊            │
│         ▲                   │
│                            │
│   Energy:                  │
│   🔋 [══●══════]           │
│      Low-ish               │
│                            │
│   Top concern right now:   │
│   [💼 Work meeting] ✓      │
│   [🧠 Racing thoughts]     │
│   [😴 Didn't sleep well]   │
│   [🏃 Physical tension]    │
│                            │
│   [Get My Recommendations] │
│                            │
│   ⏱️ 0:28 elapsed          │
│                            │
└────────────────────────────┘
```

**Marcus's Selection:** Neutral mood, low energy, work meeting anxiety
**AI Detection:** Pre-performance anxiety pattern

#### Personalized Recommendations
```
┌────────────────────────────┐
│   For your morning:        │
│                            │
│   1️⃣ Box Breathing         │
│      🕐 2 min │ 🔋 Low     │
│      "Calm pre-meeting    │
│       nerves"              │
│      [Start] [Later]       │
│                            │
│   2️⃣ 5-4-3-2-1 Grounding  │
│      🕐 3 min │ 🔋 Low     │
│      "Get present before  │
│       your day starts"     │
│      [Start] [Later]       │
│                            │
│   3️⃣ Power Pose           │
│      🕐 2 min │ 🔋 Medium  │
│      "Boost confidence    │
│       before meeting"      │
│      [Start] [Later]       │
│                            │
│   Why these? Based on your │
│   pattern: breathing works │
│   well for you on meeting  │
│   days (4/5 times helpful) │
│                            │
└────────────────────────────┘
```

**Transparency:** Explains why recommendations were made
**Learning:** AI knows his patterns from previous data

---

## 3. CRISIS DETECTION JOURNEY

### Journey Map: Alex, 20, College Student Experiencing Crisis

```
CRITICAL SAFETY FLOW (Immediate response)

Journal Entry ──▶ NLP Detection ──▶ Risk Assessment ──▶ Safety Response
      │                 │                  │                   │
      ▼                 ▼                  ▼                   ▼
  "I can't take     Keywords:          CRITICAL            Pause normal
   this anymore.    "can't take",      RISK LEVEL          interface
   Nobody would     "nobody would                          Show crisis
   even notice      notice", "give                         resources
   if I just        up"                                    immediately
   gave up."
```

### Safety Protocol Screens

#### Detection Alert (Internal, not shown to user)
```
SYSTEM ALERT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
User: Alex (ID: xxx-xxx)
Timestamp: 2025-11-16 02:34 AM
Risk Score: 0.87 (CRITICAL)

Keywords Detected:
- "can't take this anymore" (0.8)
- "nobody would notice" (0.9)
- "gave up" (0.7)

Behavioral Flags:
- Late night journaling (2:34 AM)
- 3rd consecutive low mood check-in
- Declining engagement over 5 days

IMMEDIATE ACTION REQUIRED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### User-Facing Safety Screen
```
┌────────────────────────────┐
│                            │
│    We noticed you might    │
│    be going through a      │
│    really hard time.       │
│                            │
│    ❤️ You matter.          │
│                            │
│    If you're having        │
│    thoughts of suicide,    │
│    please reach out:       │
│                            │
│  ┌────────────────────┐    │
│  │ 📞 988              │    │
│  │ Suicide & Crisis   │    │
│  │ Lifeline           │    │
│  │ Available 24/7     │    │
│  │                    │    │
│  │ [Call Now]         │    │
│  └────────────────────┘    │
│                            │
│  ┌────────────────────┐    │
│  │ 💬 Text HOME to    │    │
│  │    741741          │    │
│  │ Crisis Text Line   │    │
│  │                    │    │
│  │ [Text Now]         │    │
│  └────────────────────┘    │
│                            │
│    [See More Resources]    │
│                            │
│    [I'm Safe Right Now]    │
│                            │
└────────────────────────────┘
```

**Key Principles:**
- Immediate, clear crisis information
- Multiple contact options
- No judgment or analysis
- Always provide exit option
- Log interaction for safety

#### If User Selects "I'm Safe Right Now"
```
┌────────────────────────────┐
│                            │
│   We're glad you're safe.  │
│                            │
│   Would you like to:       │
│                            │
│   [🧘 Try a calming        │
│       exercise]            │
│                            │
│   [📝 Review your          │
│       safety plan]         │
│                            │
│   [📞 Contact someone      │
│       you trust]           │
│                            │
│   [🏠 Return to app]       │
│                            │
│   Remember: these          │
│   resources are always     │
│   available in Settings    │
│   > Safety Resources       │
│                            │
└────────────────────────────┘
```

---

## 4. ADHD EXECUTIVE FUNCTION JOURNEY

### Journey Map: Jordan, 24, Freelancer with ADHD

```
TASK BREAKDOWN FLOW

Overwhelming Task ──▶ AI Decomposition ──▶ Visual Timeline ──▶ Step-by-Step
      │                      │                    │              Completion
      ▼                      ▼                    ▼                  │
  "I need to do          Firefly breaks       Jordan sees          ▼
   my taxes but          it into 12           time needed      Dopamine hits
   I don't even          small steps          for each step    after each
   know where                                                   micro-win
   to start"
```

### Detailed Screens

#### Task Input
```
┌────────────────────────────┐
│   ADHD Task Helper         │
│                            │
│   What task feels          │
│   overwhelming?            │
│                            │
│   ┌──────────────────┐     │
│   │ Do my taxes      │     │
│   │                  │     │
│   └──────────────────┘     │
│                            │
│   How important is this?   │
│   [🔥 Urgent] [📌 Soon]    │
│   [📅 Eventually]          │
│                            │
│   About how long do you    │
│   think it'll take?        │
│   [ 2-3 hours ▾ ]          │
│                            │
│   [Break It Down For Me]   │
│                            │
└────────────────────────────┘
```

#### AI-Generated Breakdown
```
┌────────────────────────────┐
│   Your Tax Filing Plan     │
│                            │
│   Total: ~2.5 hours        │
│   (But we'll do it in      │
│    small chunks!)          │
│                            │
│   TODAY (30 min):          │
│   □ Gather W-2 forms (5m)  │
│   □ Find last year's       │
│     return (10m)           │
│   □ Create tax folder (5m) │
│   □ Take a break! (10m)    │
│                            │
│   TOMORROW (45 min):       │
│   □ Log into TurboTax (5m) │
│   □ Enter personal info    │
│     (10m)                  │
│   □ Enter W-2 #1 (15m)     │
│   □ Celebrate! 🎉 (5m)     │
│   □ Take a break (10m)     │
│                            │
│   [View Full Plan] ▼       │
│                            │
│   [Start First Step Now]   │
│                            │
└────────────────────────────┘
```

**ADHD-Friendly Features:**
- Breaks built in (prevents burnout)
- Small chunks (dopamine from completion)
- Time estimates (combats time blindness)
- Celebration moments (positive reinforcement)

#### Active Task Timer
```
┌────────────────────────────┐
│   CURRENT STEP:            │
│   Gather W-2 forms         │
│                            │
│        ⏱️ 3:24             │
│        of 5:00             │
│                            │
│   [██████████░░░]          │
│                            │
│   💡 Check: desk drawer,   │
│   email from employer,     │
│   online portal            │
│                            │
│   [✓ Done!]  [Need More    │
│               Time]        │
│                            │
│   [Pause]  [Skip Step]     │
│                            │
│   Progress: 1 of 4 steps   │
│   today completed          │
│                            │
└────────────────────────────┘
```

#### Completion Celebration
```
┌────────────────────────────┐
│                            │
│        🎉 YES! 🎉          │
│                            │
│   You completed 4 steps!   │
│                            │
│   Time spent: 28 minutes   │
│   (You estimated 30!)      │
│                            │
│   🔥🔥🔥🔥 (4 fireflies    │
│            earned)         │
│                            │
│   Your time estimation is  │
│   getting better!          │
│   Avg error: 12% (was 35%) │
│                            │
│   Tomorrow's goal:         │
│   Complete 3 more steps    │
│   (45 min total)           │
│                            │
│   [Set Reminder]           │
│                            │
│   [See My Progress]        │
│                            │
└────────────────────────────┘
```

---

## 5. AUTISM SPECTRUM SENSORY SUPPORT JOURNEY

### Journey Map: Riley, 19, Autistic College Student

```
SENSORY OVERLOAD PREVENTION

Morning Check ──▶ Sensory Load ──▶ Capacity ──▶ Proactive
    │              Assessment      Warning     Intervention
    ▼                  │              │             │
"I have a          "Rate your      "You're at   "Would you
 busy day"          current        75% sensory   like to do
                    sensory         capacity"     a regulation
                    levels"                       activity?"
```

### Sensory Dashboard
```
┌────────────────────────────┐
│   Sensory Load Monitor     │
│                            │
│   Current Capacity:        │
│   ┌──────────────────┐     │
│   │ [████████░░] 75% │     │
│   │   MONITOR ZONE   │     │
│   └──────────────────┘     │
│                            │
│   Visual Load:             │
│   [███████░░░] 70%         │
│   (Bright fluorescent      │
│    lights at school)       │
│                            │
│   Auditory Load:           │
│   [████████░░] 80%         │
│   (Cafeteria was loud)     │
│                            │
│   Social Load:             │
│   [██████░░░░] 60%         │
│   (Group project meeting)  │
│                            │
│   ⚠️ Approaching threshold │
│                            │
│   [Quick Regulation Break] │
│                            │
│   [See Today's Schedule]   │
│                            │
└────────────────────────────┘
```

#### Regulation Recommendation
```
┌────────────────────────────┐
│   Sensory Reset Needed     │
│                            │
│   Your auditory load is    │
│   high. Try:               │
│                            │
│   🎧 Noise-Canceling       │
│      Headphone Break       │
│      5 minutes             │
│                            │
│   Find a quiet spot and    │
│   wear your headphones     │
│   with no audio.           │
│                            │
│   Just silence.            │
│                            │
│   ┌──────────────────┐     │
│   │ [Start Timer]    │     │
│   └──────────────────┘     │
│                            │
│   Estimated recovery:      │
│   Auditory load will       │
│   decrease to ~50%         │
│                            │
│   [Try Different Activity] │
│                            │
└────────────────────────────┘
```

#### Emotion Identification Scaffold
```
┌────────────────────────────┐
│   What Are You Feeling?    │
│                            │
│   Sometimes emotions are   │
│   hard to name. Let's      │
│   start with your body:    │
│                            │
│   Where do you feel        │
│   something physical?      │
│                            │
│     [Head: pressure]       │
│         ○                  │
│        /|\                 │
│   [Chest:    [Stomach:     │
│    tight]     butterflies] │
│        / \                 │
│   [Hands:    [Legs:        │
│    restless]  heavy]       │
│                            │
│   Based on "chest tight"   │
│   + "head pressure":       │
│                            │
│   This might be:           │
│   [😰 Anxiety] [😠 Anger]  │
│   [😔 Sadness] [🤔 Not     │
│                   sure]    │
│                            │
└────────────────────────────┘
```

---

## 6. WEEKLY SUMMARY JOURNEY

### Every Sunday Evening: Reflection and Planning

```
┌────────────────────────────────────────────────────────────┐
│                    YOUR WEEK IN REVIEW                      │
│                    Nov 10 - Nov 16, 2025                   │
└────────────────────────────────────────────────────────────┘

📊 MOOD JOURNEY
┌─────────────────────────────────────────┐
│ 10  ·                                   │
│  9  ·        ●                          │
│  8  ·     ●     ●                       │
│  7  ·  ●                 ●     ●        │
│  6  ●                       ●           │
│  5  ·                                   │
│     Mon  Tue  Wed  Thu  Fri  Sat  Sun   │
└─────────────────────────────────────────┘
Trend: Gradually improving 📈

🎯 KEY INSIGHTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Best time for check-ins: 8:30 AM
  (You were most consistent then)

• Most effective technique: Box Breathing
  (Rated helpful 4 out of 5 times)

• Energy peak: Afternoons 2-4 PM
  (Consider scheduling important tasks then)

• Trigger identified: Pre-meeting anxiety
  (Appeared 3 times this week)

🏆 ACHIEVEMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ 7-day check-in streak! 🔥
✓ Tried 12 different interventions
✓ Completed 3 DBT skills
✓ Time estimation improved by 15%

🌱 NEXT WEEK'S FOCUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Suggestion: Practice "Opposite Action" when
feeling withdrawal urge. This DBT skill has
shown good results for users with your pattern.

[Set This as Weekly Goal]

🔥 FIREFLY GARDEN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You earned 18 fireflies this week!
Your garden is growing beautifully.

[Visit Your Garden] ✨

[Share Progress] (Anonymized to community)
[Export Report] (PDF for therapist)
```

---

## 7. USER JOURNEY METRICS

### Critical Success Factors

| Journey Stage | Target Metric | Current Industry Avg | Firefly Target |
|--------------|---------------|---------------------|----------------|
| Onboarding completion | % complete setup | 40% | 85% |
| First check-in | Within 24 hours | 60% | 95% |
| 7-day retention | Active after week 1 | 25% | 65% |
| 30-day retention | Active after month 1 | 10% | 45% |
| Intervention completion | % finish started | 50% | 80% |
| Positive feedback rate | Helped/very helpful | 60% | 75% |
| Crisis response time | Minutes to resources | 5+ min | < 30 sec |
| Weekly summary views | % users open | 20% | 70% |

### Continuous Improvement Loop

```
User Feedback ──▶ Data Analysis ──▶ Hypothesis ──▶ A/B Test
      ▲                                              │
      │                                              │
      └───────────────── Results ◀──────────────────┘
```

Every user interaction feeds back into improving recommendations, UI/UX, and intervention effectiveness.

---

**These user journeys form the foundation for building an empathetic, effective, and engaging mental wellness platform.**
