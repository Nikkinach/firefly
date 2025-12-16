# Machine Learning Module for Firefly

This module provides advanced ML/NLP capabilities for mental health tracking and prediction.

## Features

### 1. Natural Language Processing (NLP)

#### Sentiment Analysis
- Fine-tuned BERT model for sentiment detection
- Returns normalized score (0.0-1.0) and label (positive/neutral/negative)
- Handles long text by analyzing both beginning and end

#### Emotion Classification
- Detects 7 emotions: anger, disgust, fear, joy, neutral, sadness, surprise
- Uses DistilRoBERTa model fine-tuned on emotion data
- Returns confidence scores for all emotions

#### Crisis Detection
- Multi-level keyword detection (critical, high, moderate, low)
- Weighted severity scoring
- Zero-shot classification for context understanding
- Automatic alerts for high-risk entries
- **IMPORTANT**: This is a supportive tool, not a replacement for professional help

#### Theme Extraction
- LDA topic modeling for pattern identification
- Extracts recurring themes from journal entries
- Requires minimum 3 entries for analysis

### 2. Advanced Prediction Models

#### LSTM Mood Forecasting
- 3-layer LSTM architecture with dropout
- Predicts mood up to 7 days ahead
- Monte Carlo dropout for confidence intervals
- Requires minimum 21 days of training data

#### Seasonal Pattern Detection
- Weekly pattern analysis (best/worst days)
- Monthly trends (beginning/middle/end)
- Yearly seasonality (best/worst months)
- FFT-based frequency detection for custom cycles

#### Weather Correlation
- Pearson correlation with weather factors
- Analyzes: temperature, precipitation, humidity, pressure, cloud cover
- Statistical significance testing
- Requires minimum 30 days of combined data

#### Sleep Pattern Analysis
- Sleep duration correlation with mood
- Sleep quality impact assessment
- Optimal sleep range detection
- Sleep consistency scoring
- Requires minimum 14 days of data

### 3. Collaborative Filtering

#### User Clustering
- Anonymized user profiling
- K-means or DBSCAN clustering
- Feature extraction from mood patterns
- Privacy-preserving design

#### Intervention Recommendations
- Learn from similar users' successes
- Weighted effectiveness scoring
- Confidence-based ranking
- Fallback to general recommendations

#### A/B Testing Framework
- Create and manage experiments
- Balanced variant assignment
- Statistical significance testing
- T-test for 2-variant comparison

## Installation

### Dependencies

```bash
pip install transformers torch scikit-learn tensorflow nltk textblob scipy sentencepiece accelerate
```

Or use the updated requirements.txt:

```bash
pip install -r requirements.txt
```

### Database Migration

Create migration for ML models:

```bash
alembic revision --autogenerate -m "Add ML models"
alembic upgrade head
```

## Usage

### API Integration

Add the ML router to your FastAPI app:

```python
from app.ml.api import router as ml_router

app.include_router(ml_router)
```

### API Endpoints

#### NLP Analysis

```http
POST /ml/analyze-journal
Content-Type: application/json

{
  "text": "I feel really happy today...",
  "journal_entry_id": 123
}
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
    "primary_score": 0.87,
    "all_emotions": {...}
  },
  "crisis_detection": {
    "crisis_detected": false,
    "risk_level": "none",
    ...
  },
  "themes": {...}
}
```

#### Mood Prediction

1. Train model (one-time):
```http
POST /ml/train-model
{
  "model_type": "lstm",
  "sequence_length": 14,
  "epochs": 50
}
```

2. Get predictions:
```http
POST /ml/predict-mood
{
  "days_ahead": 7,
  "include_confidence": true
}
```

#### Seasonal Patterns

```http
GET /ml/seasonal-patterns
```

Returns weekly, monthly, and yearly patterns if sufficient data exists.

#### Recommendations

```http
POST /ml/recommend-interventions
{
  "available_interventions": [
    {
      "id": "meditation_1",
      "name": "Guided Meditation",
      "description": "10-minute mindfulness meditation",
      "category": "mindfulness"
    }
  ],
  "n_recommendations": 5
}
```

#### Record Effectiveness

```http
POST /ml/record-effectiveness
{
  "intervention_id": "meditation_1",
  "effectiveness_score": 0.8,
  "mood_before": 5.0,
  "mood_after": 7.5
}
```

#### A/B Testing

Create test:
```http
POST /ml/ab-test/create
{
  "test_name": "Meditation vs Journaling",
  "variants": [
    {"id": "meditation", "config": {...}},
    {"id": "journaling", "config": {...}}
  ],
  "target_metric": "mood_improvement",
  "duration_days": 30
}
```

Analyze results:
```http
GET /ml/ab-test/{test_id}/analyze
```

## Service Architecture

### NLPService
- Singleton pattern for model efficiency
- Lazy loading of transformer models
- Automatic NLTK data download
- Error handling and fallbacks

### PredictionService
- LSTM and Transformer model support
- Automatic feature engineering
- Confidence interval calculation
- Pattern detection algorithms

### CollaborativeFilteringService
- Privacy-first design (SHA-256 anonymization)
- Cosine similarity for user matching
- Weighted recommendation scoring
- A/B test statistical analysis

## Privacy & Security

### Anonymization
- User IDs are hashed with SHA-256
- Only behavioral features stored (no personal data)
- Cluster-based aggregation for privacy
- No reverse-engineering of user identity

### Crisis Detection
- Automatic alerts for high-risk content
- Multi-level severity classification
- Integration with support resources recommended
- Should be paired with professional monitoring

## Performance Considerations

### Model Loading
- Models loaded on first use (lazy initialization)
- Singleton pattern prevents duplicate loading
- GPU acceleration if available (CUDA)
- CPU fallback for compatibility

### Batch Processing
- Recommended for large-scale analysis
- Can process multiple entries concurrently
- Database transactions for consistency

### Scaling
- Consider model serving infrastructure (TensorFlow Serving, TorchServe)
- Cache predictions for performance
- Background task processing for training (Celery)

## Error Handling

All endpoints return standardized error responses:

```json
{
  "success": false,
  "error": "Description of error"
}
```

Common errors:
- Insufficient data for training/analysis
- Model not trained
- Invalid input format
- Service initialization failure

## Future Enhancements

- [ ] Transformer model for time series (currently LSTM only)
- [ ] Multi-modal analysis (combine text + numerical data)
- [ ] Real-time streaming predictions
- [ ] Federated learning for privacy
- [ ] Explainable AI features
- [ ] Multi-language support
- [ ] Custom model fine-tuning per user

## References

- **Sentiment**: nlptown/bert-base-multilingual-uncased-sentiment
- **Emotion**: j-hartmann/emotion-english-distilroberta-base
- **Zero-shot**: facebook/bart-large-mnli
- **LSTM**: Custom architecture (3-layer)
- **Clustering**: K-means, DBSCAN (scikit-learn)

## Support

For issues or questions about the ML module:
1. Check logs for detailed error messages
2. Verify minimum data requirements
3. Ensure dependencies are correctly installed
4. Check GPU/CUDA compatibility if using GPU acceleration

## License

Part of the Firefly mental health tracking platform.
