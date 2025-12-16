# ML Module Quick Start Guide

Get started with Firefly's advanced ML features in minutes.

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- transformers, torch (for NLP)
- tensorflow, keras (for predictions)
- scikit-learn (for ML algorithms)
- scipy, pandas, numpy (for data processing)

### 2. Run Setup Script

```bash
python -m app.ml.setup --test
```

This will:
- Download NLTK data
- Download transformer models (may take 5-10 minutes)
- Create necessary directories
- Run a quick test

For faster setup (skip model downloads):
```bash
python -m app.ml.setup --skip-models
```

### 3. Run Database Migration

```bash
alembic upgrade head
```

## Integration

### Add ML Router to Your App

Edit `app/main.py`:

```python
from app.ml.api import router as ml_router

app.include_router(ml_router)
```

### Start the Server

```bash
uvicorn app.main:app --reload
```

## Quick Examples

### 1. Analyze a Journal Entry

```bash
curl -X POST "http://localhost:8000/ml/analyze-journal" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I feel really happy and motivated today. Accomplished a lot at work and spent quality time with friends."
  }'
```

Response:
```json
{
  "sentiment": {
    "score": 0.85,
    "label": "positive",
    "confidence": 0.92
  },
  "emotions": {
    "primary_emotion": "joy",
    "primary_score": 0.87
  },
  "crisis_detection": {
    "crisis_detected": false,
    "risk_level": "none"
  }
}
```

### 2. Check ML Services Health

```bash
curl "http://localhost:8000/ml/health"
```

### 3. Train Prediction Model

Requires at least 21 days of mood data:

```bash
curl -X POST "http://localhost:8000/ml/train-model" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_type": "lstm",
    "sequence_length": 14,
    "epochs": 50
  }'
```

### 4. Get Mood Predictions

```bash
curl -X POST "http://localhost:8000/ml/predict-mood" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "days_ahead": 7,
    "include_confidence": true
  }'
```

### 5. Detect Seasonal Patterns

```bash
curl "http://localhost:8000/ml/seasonal-patterns" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Get Personalized Recommendations

```bash
curl -X POST "http://localhost:8000/ml/recommend-interventions" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "available_interventions": [
      {
        "id": "meditation_1",
        "name": "Guided Meditation",
        "description": "10-minute mindfulness practice",
        "category": "mindfulness"
      },
      {
        "id": "exercise_1",
        "name": "Morning Walk",
        "description": "30-minute outdoor walk",
        "category": "physical"
      }
    ],
    "n_recommendations": 3
  }'
```

## Common Use Cases

### Crisis Detection Alert System

Monitor for high-risk journal entries:

```python
from app.ml.nlp_service import get_nlp_service

nlp = get_nlp_service()
analysis = await nlp.analyze_journal_entry(journal_text)

if analysis['crisis_detection']['requires_immediate_attention']:
    # Send alert to support team
    # Display crisis resources to user
    send_crisis_alert(user_id, analysis)
```

### Mood Forecasting Dashboard

Show users their predicted mood trend:

```python
from app.ml.prediction_service import get_prediction_service

predictor = get_prediction_service()
predictions = await predictor.predict_mood(
    recent_data=user_mood_history,
    days_ahead=7
)

# Display in frontend chart
return {
    'predictions': predictions['predictions'],
    'confidence_intervals': True
}
```

### Smart Intervention Recommendations

Recommend interventions based on similar users:

```python
from app.ml.collaborative_filtering import get_collaborative_filtering_service

cf = get_collaborative_filtering_service()
recommendations = await cf.recommend_interventions(
    user_id=current_user_id,
    available_interventions=all_interventions,
    n_recommendations=5
)

# Show top recommendations
for rec in recommendations['recommendations']:
    print(f"{rec['intervention']['name']}: {rec['score']:.2f}")
```

## Performance Tips

### 1. GPU Acceleration

If you have a CUDA-compatible GPU:

```bash
# Verify GPU is available
python -c "import torch; print(torch.cuda.is_available())"
```

Models will automatically use GPU if available.

### 2. Background Processing

For batch analysis, use Celery tasks:

```python
from celery import Celery

@celery.task
def analyze_journal_batch(journal_ids):
    nlp = get_nlp_service()
    results = []
    for journal_id in journal_ids:
        entry = get_journal_entry(journal_id)
        analysis = await nlp.analyze_journal_entry(entry.text)
        results.append(analysis)
    return results
```

### 3. Model Caching

Models are cached after first load. First request may be slow:

```python
# Warm up models on startup
async def startup_event():
    nlp = get_nlp_service()
    # Models are now loaded
```

## Troubleshooting

### Model Download Fails

```bash
# Set HuggingFace cache directory
export TRANSFORMERS_CACHE=/path/to/cache

# Retry download
python -m app.ml.setup
```

### Out of Memory

For CPU-only or low-memory systems:

```python
# In config.py
config.nlp.use_gpu = False
config.prediction.batch_size = 8  # Reduce batch size
```

### Slow Predictions

```bash
# Use lighter models
config.nlp.sentiment_model = "distilbert-base-uncased"  # Faster alternative
```

## Next Steps

1. **Frontend Integration**: Build UI for ML features
2. **Real-time Alerts**: Set up WebSocket for crisis alerts
3. **Scheduled Jobs**: Run pattern detection weekly
4. **A/B Testing**: Test new intervention effectiveness
5. **Custom Models**: Fine-tune on your specific data

## API Documentation

Full API docs available at:
```
http://localhost:8000/docs#/Machine%20Learning
```

## Support

- Check logs: `logs/ml_service.log`
- GitHub Issues: [Report bugs](https://github.com/yourusername/firefly/issues)
- Documentation: See `README.md` for detailed info

## Data Requirements

| Feature | Minimum Data | Recommended |
|---------|-------------|-------------|
| NLP Analysis | 1 entry | Any amount |
| Mood Prediction | 21 days | 60+ days |
| Seasonal Patterns | 90 days | 180+ days |
| Weather Correlation | 30 days | 90+ days |
| Sleep Analysis | 14 days | 30+ days |
| Collaborative Filtering | 10 users | 100+ users |

## Privacy & Ethics

- All user data is anonymized (SHA-256 hashing)
- Crisis detection is supportive, not diagnostic
- Recommendations are suggestions, not medical advice
- Users control their data and can opt-out anytime
- Compliant with HIPAA/GDPR standards

## Example Workflow

```python
# 1. User writes journal entry
journal = create_journal_entry(text="Today was challenging...")

# 2. Analyze with NLP
analysis = await nlp.analyze_journal_entry(journal.text)
save_analysis(journal.id, analysis)

# 3. Check for crisis
if analysis['crisis_detection']['requires_immediate_attention']:
    show_crisis_resources(user)
    notify_support_team(user, analysis)

# 4. Update user profile
update_user_profile(user.id, journal.mood_score)

# 5. Get recommendations
recs = await cf.recommend_interventions(user.id, interventions)

# 6. Show personalized suggestions
display_recommendations(recs)

# 7. Track effectiveness
if user_completes_intervention(intervention_id):
    record_effectiveness(user.id, intervention_id, effectiveness)
```

Ready to build the future of mental health tracking! 🚀
