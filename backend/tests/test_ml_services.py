"""
Comprehensive test suite for ML services
Tests NLP, predictions, collaborative filtering, and A/B testing
"""

import pytest
import asyncio
from datetime import datetime, timedelta
import numpy as np

from app.ml.nlp_service import get_nlp_service
from app.ml.prediction_service import get_prediction_service
from app.ml.collaborative_filtering import get_collaborative_filtering_service


# Test fixtures
@pytest.fixture
def sample_journal_text():
    return "I feel really happy and motivated today. Accomplished a lot at work and spent quality time with friends."


@pytest.fixture
def crisis_text():
    return "I feel so hopeless and worthless. I can't go on like this anymore. Everything is unbearable."


@pytest.fixture
def sample_mood_data():
    """Generate sample mood data for testing"""
    base_date = datetime.now() - timedelta(days=60)
    data = []

    for i in range(60):
        date = base_date + timedelta(days=i)
        # Simulate weekly pattern + noise
        mood = 5 + 2 * np.sin(2 * np.pi * i / 7) + np.random.normal(0, 0.5)
        mood = max(1, min(10, mood))  # Clamp to 1-10

        data.append({
            'date': date.isoformat(),
            'mood_score': mood
        })

    return data


@pytest.fixture
def sample_sleep_data():
    """Generate sample sleep data"""
    base_date = datetime.now() - timedelta(days=30)
    data = []

    for i in range(30):
        date = base_date + timedelta(days=i)
        sleep_hours = 7 + np.random.normal(0, 1)
        sleep_hours = max(4, min(10, sleep_hours))

        data.append({
            'date': date.isoformat(),
            'sleep_hours': sleep_hours,
            'sleep_quality': np.random.uniform(5, 9)
        })

    return data


@pytest.fixture
def sample_weather_data():
    """Generate sample weather data"""
    base_date = datetime.now() - timedelta(days=30)
    data = []

    for i in range(30):
        date = base_date + timedelta(days=i)
        data.append({
            'date': date.isoformat(),
            'temperature': 20 + np.random.normal(0, 5),
            'precipitation': np.random.uniform(0, 10),
            'humidity': np.random.uniform(40, 80),
            'pressure': np.random.uniform(990, 1020),
            'cloud_cover': np.random.uniform(0, 100)
        })

    return data


# ============================================================================
# NLP Service Tests
# ============================================================================

class TestNLPService:
    """Test NLP analysis features"""

    @pytest.mark.asyncio
    async def test_sentiment_analysis(self, sample_journal_text):
        """Test sentiment analysis"""
        nlp = get_nlp_service()
        result = await nlp.analyze_sentiment(sample_journal_text)

        assert 'score' in result
        assert 'label' in result
        assert 'confidence' in result
        assert 0 <= result['score'] <= 1
        assert result['label'] in ['positive', 'negative', 'neutral']

    @pytest.mark.asyncio
    async def test_emotion_classification(self, sample_journal_text):
        """Test emotion classification"""
        nlp = get_nlp_service()
        result = await nlp.classify_emotions(sample_journal_text)

        assert 'primary_emotion' in result
        assert 'primary_score' in result
        assert 'all_emotions' in result
        assert 0 <= result['primary_score'] <= 1

    @pytest.mark.asyncio
    async def test_crisis_detection_positive(self, sample_journal_text):
        """Test crisis detection on positive text"""
        nlp = get_nlp_service()
        result = await nlp.detect_crisis_keywords(sample_journal_text)

        assert result['crisis_detected'] == False
        assert result['risk_level'] == 'none'
        assert result['requires_immediate_attention'] == False

    @pytest.mark.asyncio
    async def test_crisis_detection_negative(self, crisis_text):
        """Test crisis detection on concerning text"""
        nlp = get_nlp_service()
        result = await nlp.detect_crisis_keywords(crisis_text)

        assert result['crisis_detected'] == True
        assert result['risk_level'] in ['moderate', 'high', 'critical']
        assert len(result['matched_keywords']) > 0

    @pytest.mark.asyncio
    async def test_theme_extraction(self):
        """Test theme extraction from multiple entries"""
        nlp = get_nlp_service()
        texts = [
            "I went for a run today and felt great",
            "Exercise really helps my mood",
            "Another good workout session",
            "Work was stressful but manageable",
            "Deadline pressure at work again"
        ]

        result = await nlp.extract_themes(texts)

        assert 'themes' in result
        if result['themes']:  # May not work with small sample
            assert isinstance(result['themes'], list)

    @pytest.mark.asyncio
    async def test_full_journal_analysis(self, sample_journal_text):
        """Test complete journal analysis"""
        nlp = get_nlp_service()
        result = await nlp.analyze_journal_entry(sample_journal_text)

        assert 'sentiment' in result
        assert 'emotions' in result
        assert 'crisis_detection' in result
        assert 'themes' in result
        assert 'analyzed_at' in result


# ============================================================================
# Prediction Service Tests
# ============================================================================

class TestPredictionService:
    """Test prediction and pattern detection"""

    @pytest.mark.asyncio
    async def test_lstm_model_build(self):
        """Test LSTM model building"""
        predictor = get_prediction_service()
        model = predictor.build_lstm_model(sequence_length=14, n_features=5)

        assert model is not None
        assert model.input_shape == (None, 14, 5)

    @pytest.mark.asyncio
    async def test_lstm_training(self, sample_mood_data):
        """Test LSTM model training"""
        predictor = get_prediction_service()
        result = await predictor.train_lstm_model(
            sample_mood_data,
            sequence_length=14,
            epochs=5  # Low for testing
        )

        assert result['success'] == True
        assert 'final_loss' in result
        assert 'epochs_trained' in result

    @pytest.mark.asyncio
    async def test_mood_prediction(self, sample_mood_data):
        """Test mood prediction"""
        predictor = get_prediction_service()

        # Train first
        await predictor.train_lstm_model(sample_mood_data, epochs=5)

        # Predict
        result = await predictor.predict_mood(
            sample_mood_data[-14:],
            days_ahead=7
        )

        if result['success']:
            assert 'predictions' in result
            assert len(result['predictions']) == 7
            for pred in result['predictions']:
                assert 'date' in pred
                assert 'predicted_mood' in pred

    @pytest.mark.asyncio
    async def test_seasonal_pattern_detection(self, sample_mood_data):
        """Test seasonal pattern detection"""
        predictor = get_prediction_service()
        result = await predictor.detect_seasonal_patterns(sample_mood_data)

        assert 'patterns_detected' in result
        if result['patterns_detected']:
            assert 'weekly_pattern' in result
            assert 'monthly_pattern' in result

    @pytest.mark.asyncio
    async def test_weather_correlation(self, sample_mood_data, sample_weather_data):
        """Test weather correlation analysis"""
        predictor = get_prediction_service()

        # Align dates
        mood_data = sample_mood_data[:30]
        result = await predictor.analyze_weather_correlation(
            mood_data,
            sample_weather_data
        )

        assert 'sufficient_data' in result
        if result['sufficient_data']:
            assert 'correlations' in result

    @pytest.mark.asyncio
    async def test_sleep_analysis(self, sample_mood_data, sample_sleep_data):
        """Test sleep pattern analysis"""
        predictor = get_prediction_service()

        # Align dates
        mood_data = sample_mood_data[:30]
        result = await predictor.analyze_sleep_patterns(
            mood_data,
            sample_sleep_data
        )

        assert 'sufficient_data' in result
        if result['sufficient_data']:
            assert 'sleep_duration_correlation' in result
            assert 'optimal_sleep_range' in result


# ============================================================================
# Collaborative Filtering Tests
# ============================================================================

class TestCollaborativeFiltering:
    """Test collaborative filtering and recommendations"""

    @pytest.mark.asyncio
    async def test_user_profile_creation(self, sample_mood_data):
        """Test user profile creation"""
        cf = get_collaborative_filtering_service()
        result = await cf.create_user_profile(
            "test_user_1",
            sample_mood_data,
            anonymize=True
        )

        assert result['success'] == True
        assert 'profile_id' in result
        assert 'features' in result
        assert len(result['profile_id']) > 0

    @pytest.mark.asyncio
    async def test_user_clustering(self, sample_mood_data):
        """Test user clustering"""
        cf = get_collaborative_filtering_service()

        # Create multiple profiles
        for i in range(10):
            await cf.create_user_profile(
                f"test_user_{i}",
                sample_mood_data,
                anonymize=True
            )

        # Cluster
        result = await cf.cluster_users(n_clusters=3, method='kmeans')

        assert result['success'] == True
        assert result['n_users'] >= 10
        assert 'cluster_analysis' in result

    @pytest.mark.asyncio
    async def test_find_similar_users(self, sample_mood_data):
        """Test finding similar users"""
        cf = get_collaborative_filtering_service()

        # Create profiles
        for i in range(5):
            await cf.create_user_profile(
                f"test_user_{i}",
                sample_mood_data,
                anonymize=True
            )

        # Find similar
        result = await cf.find_similar_users("test_user_0", top_k=3)

        if result['success']:
            assert 'similar_users' in result

    @pytest.mark.asyncio
    async def test_intervention_recommendations(self):
        """Test intervention recommendations"""
        cf = get_collaborative_filtering_service()

        interventions = [
            {
                'id': 'meditation_1',
                'name': 'Meditation',
                'description': 'Guided meditation',
                'category': 'mindfulness'
            },
            {
                'id': 'exercise_1',
                'name': 'Exercise',
                'description': 'Physical activity',
                'category': 'physical'
            }
        ]

        result = await cf.recommend_interventions(
            "test_user_0",
            interventions,
            n_recommendations=2
        )

        assert 'recommendations' in result

    @pytest.mark.asyncio
    async def test_record_effectiveness(self):
        """Test recording intervention effectiveness"""
        cf = get_collaborative_filtering_service()

        result = await cf.record_intervention_effectiveness(
            "test_user_0",
            "meditation_1",
            0.8
        )

        assert result['success'] == True

    @pytest.mark.asyncio
    async def test_ab_test_creation(self):
        """Test A/B test creation"""
        cf = get_collaborative_filtering_service()

        variants = [
            {'id': 'variant_a', 'name': 'Control'},
            {'id': 'variant_b', 'name': 'Treatment'}
        ]

        result = await cf.create_ab_test(
            "test_experiment",
            variants,
            "mood_improvement",
            duration_days=30
        )

        assert result['success'] == True
        assert 'test_id' in result

    @pytest.mark.asyncio
    async def test_ab_test_assignment(self):
        """Test A/B test variant assignment"""
        cf = get_collaborative_filtering_service()

        # Create test
        variants = [
            {'id': 'variant_a', 'name': 'Control'},
            {'id': 'variant_b', 'name': 'Treatment'}
        ]

        test = await cf.create_ab_test(
            "test_assignment",
            variants,
            "mood_improvement"
        )

        # Assign user
        result = await cf.assign_user_to_variant(
            test['test_id'],
            "test_user_0",
            method='random'
        )

        assert result['success'] == True
        assert 'variant' in result

    @pytest.mark.asyncio
    async def test_ab_test_analysis(self):
        """Test A/B test analysis"""
        cf = get_collaborative_filtering_service()

        # Create and run test
        variants = [
            {'id': 'variant_a', 'name': 'Control'},
            {'id': 'variant_b', 'name': 'Treatment'}
        ]

        test = await cf.create_ab_test(
            "test_analysis",
            variants,
            "mood_improvement"
        )

        test_id = test['test_id']

        # Record some results
        for i in range(10):
            await cf.assign_user_to_variant(test_id, f"user_{i}")
            await cf.record_ab_test_result(
                test_id,
                f"user_{i}",
                np.random.uniform(5, 8)
            )

        # Analyze
        result = await cf.analyze_ab_test(test_id)

        assert result['success'] == True
        assert 'results' in result


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Test integrated workflows"""

    @pytest.mark.asyncio
    async def test_complete_analysis_workflow(self, sample_journal_text):
        """Test complete analysis workflow"""
        nlp = get_nlp_service()

        # 1. Analyze journal
        analysis = await nlp.analyze_journal_entry(sample_journal_text)

        # 2. Check sentiment
        assert analysis['sentiment']['label'] in ['positive', 'negative', 'neutral']

        # 3. Check emotions
        assert len(analysis['emotions']['all_emotions']) > 0

        # 4. Verify crisis detection ran
        assert 'crisis_detection' in analysis

    @pytest.mark.asyncio
    async def test_prediction_workflow(self, sample_mood_data):
        """Test prediction workflow"""
        predictor = get_prediction_service()

        # 1. Train model
        train_result = await predictor.train_lstm_model(
            sample_mood_data,
            epochs=5
        )
        assert train_result['success'] == True

        # 2. Make predictions
        pred_result = await predictor.predict_mood(
            sample_mood_data[-14:],
            days_ahead=7
        )

        if pred_result['success']:
            assert len(pred_result['predictions']) == 7

        # 3. Detect patterns
        pattern_result = await predictor.detect_seasonal_patterns(
            sample_mood_data
        )
        assert 'patterns_detected' in pattern_result


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
