"""
Comprehensive ML Testing Script
Tests all ML functionalities with dummy data
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import logging

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ml.nlp_service import get_nlp_service
from app.ml.prediction_service import get_prediction_service
from app.ml.collaborative_filtering import get_collaborative_filtering_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MLTester:
    """Comprehensive ML testing suite"""

    def __init__(self):
        self.nlp_service = None
        self.prediction_service = None
        self.cf_service = None
        self.test_results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }

    async def setup_services(self):
        """Initialize ML services"""
        logger.info("=" * 80)
        logger.info("INITIALIZING ML SERVICES")
        logger.info("=" * 80)

        try:
            self.nlp_service = get_nlp_service()
            logger.info("✓ NLP Service initialized")

            self.prediction_service = get_prediction_service()
            logger.info("✓ Prediction Service initialized")

            self.cf_service = get_collaborative_filtering_service()
            logger.info("✓ Collaborative Filtering Service initialized")

            return True
        except Exception as e:
            logger.error(f"✗ Service initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ========================================================================
    # DATA GENERATION
    # ========================================================================

    def generate_mood_data(self, days=60, user_pattern='normal'):
        """Generate realistic mood data"""
        base_date = datetime.now() - timedelta(days=days)
        data = []

        for i in range(days):
            date = base_date + timedelta(days=i)

            # Different patterns for different users
            if user_pattern == 'normal':
                # Weekly pattern + some noise
                mood = 6 + 2 * np.sin(2 * np.pi * i / 7) + np.random.normal(0, 0.8)
            elif user_pattern == 'improving':
                # Upward trend
                mood = 4 + (i / days) * 4 + np.random.normal(0, 0.5)
            elif user_pattern == 'declining':
                # Downward trend
                mood = 8 - (i / days) * 3 + np.random.normal(0, 0.5)
            elif user_pattern == 'volatile':
                # High volatility
                mood = 5 + np.random.normal(0, 2)
            else:
                mood = 5 + np.random.normal(0, 1)

            # Clamp to 1-10
            mood = max(1, min(10, mood))

            data.append({
                'date': date.isoformat(),
                'mood_score': float(mood)
            })

        return data

    def generate_journal_texts(self):
        """Generate sample journal texts for testing"""
        return {
            'positive': [
                "I feel amazing today! Had a great workout and caught up with an old friend. Life is good.",
                "Really proud of what I accomplished at work today. Feeling motivated and energized.",
                "Beautiful weather, spent time in nature. Feeling peaceful and grateful."
            ],
            'neutral': [
                "Normal day today. Nothing special happened. Just going through the motions.",
                "Work was okay. Had some meetings. Made dinner. Regular Tuesday.",
                "Felt pretty average today. Some ups and downs but mostly balanced."
            ],
            'negative': [
                "Feeling really down today. Everything seems overwhelming and difficult.",
                "Had a rough day. Feeling stressed and anxious about everything.",
                "Not in a good place mentally. Struggling to find motivation."
            ],
            'crisis': [
                "I feel so hopeless. I don't see a way out of this situation.",
                "Everything is unbearable. I can't keep going like this anymore.",
                "Feeling completely worthless and alone. Can't see any reason to continue."
            ]
        }

    def generate_sleep_data(self, days=30):
        """Generate sleep data"""
        base_date = datetime.now() - timedelta(days=days)
        data = []

        for i in range(days):
            date = base_date + timedelta(days=i)

            # Simulate sleep patterns
            base_sleep = 7
            weekend_bonus = 1 if date.weekday() >= 5 else 0
            sleep_hours = base_sleep + weekend_bonus + np.random.normal(0, 0.8)
            sleep_hours = max(4, min(10, sleep_hours))

            sleep_quality = 5 + sleep_hours * 0.5 + np.random.normal(0, 0.5)
            sleep_quality = max(1, min(10, sleep_quality))

            data.append({
                'date': date.isoformat(),
                'sleep_hours': float(sleep_hours),
                'sleep_quality': float(sleep_quality)
            })

        return data

    def generate_weather_data(self, days=30):
        """Generate weather data"""
        base_date = datetime.now() - timedelta(days=days)
        data = []

        for i in range(days):
            date = base_date + timedelta(days=i)

            # Simulate weather patterns
            temp_base = 20
            temp_variation = 10 * np.sin(2 * np.pi * i / 365)
            temperature = temp_base + temp_variation + np.random.normal(0, 3)

            data.append({
                'date': date.isoformat(),
                'temperature': float(temperature),
                'precipitation': float(max(0, np.random.exponential(2))),
                'humidity': float(np.random.uniform(30, 90)),
                'pressure': float(np.random.uniform(980, 1030)),
                'cloud_cover': float(np.random.uniform(0, 100))
            })

        return data

    # ========================================================================
    # NLP TESTS
    # ========================================================================

    async def test_nlp_sentiment_analysis(self):
        """Test sentiment analysis"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Sentiment Analysis")
        logger.info("=" * 80)

        texts = self.generate_journal_texts()

        for category, samples in texts.items():
            logger.info(f"\nTesting {category} texts:")

            for text in samples:
                try:
                    result = await self.nlp_service.analyze_sentiment(text)

                    logger.info(f"  Text: {text[:50]}...")
                    logger.info(f"  Sentiment: {result['label']} (score: {result['score']:.2f}, confidence: {result['confidence']:.2f})")

                    # Validate
                    assert 0 <= result['score'] <= 1, "Score out of range"
                    assert result['label'] in ['positive', 'negative', 'neutral'], "Invalid label"

                    self.test_results['passed'].append(f"Sentiment analysis: {category}")

                except Exception as e:
                    logger.error(f"  ✗ Failed: {e}")
                    self.test_results['failed'].append(f"Sentiment analysis: {category} - {e}")
                    return False

        logger.info("\n✓ Sentiment analysis tests PASSED")
        return True

    async def test_nlp_emotion_classification(self):
        """Test emotion classification"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Emotion Classification")
        logger.info("=" * 80)

        texts = self.generate_journal_texts()

        for category, samples in texts.items():
            logger.info(f"\nTesting {category} texts:")

            for text in samples[:1]:  # Test one from each category
                try:
                    result = await self.nlp_service.classify_emotions(text)

                    logger.info(f"  Text: {text[:50]}...")
                    logger.info(f"  Primary emotion: {result['primary_emotion']} (score: {result['primary_score']:.2f})")
                    logger.info(f"  All emotions: {list(result['all_emotions'].keys())}")

                    # Validate
                    assert 0 <= result['primary_score'] <= 1, "Score out of range"
                    assert isinstance(result['all_emotions'], dict), "Invalid emotions dict"

                    self.test_results['passed'].append(f"Emotion classification: {category}")

                except Exception as e:
                    logger.error(f"  ✗ Failed: {e}")
                    self.test_results['failed'].append(f"Emotion classification: {category} - {e}")
                    return False

        logger.info("\n✓ Emotion classification tests PASSED")
        return True

    async def test_nlp_crisis_detection(self):
        """Test crisis keyword detection"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Crisis Detection")
        logger.info("=" * 80)

        texts = self.generate_journal_texts()

        # Test positive text (should not detect crisis)
        logger.info("\nTesting positive text:")
        result = await self.nlp_service.detect_crisis_keywords(texts['positive'][0])
        logger.info(f"  Crisis detected: {result['crisis_detected']}")
        logger.info(f"  Risk level: {result['risk_level']}")
        assert result['crisis_detected'] == False, "False positive crisis detection"
        assert result['risk_level'] == 'none', "Incorrect risk level"
        self.test_results['passed'].append("Crisis detection: positive text")

        # Test crisis text (should detect)
        logger.info("\nTesting crisis text:")
        result = await self.nlp_service.detect_crisis_keywords(texts['crisis'][0])
        logger.info(f"  Crisis detected: {result['crisis_detected']}")
        logger.info(f"  Risk level: {result['risk_level']}")
        logger.info(f"  Crisis score: {result['crisis_score']:.2f}")
        logger.info(f"  Matched keywords: {len(result['matched_keywords'])} keywords")
        logger.info(f"  Requires attention: {result['requires_immediate_attention']}")

        assert result['crisis_detected'] == True, "Failed to detect crisis"
        assert result['risk_level'] in ['moderate', 'high', 'critical'], "Incorrect risk level"
        assert len(result['matched_keywords']) > 0, "No keywords matched"

        self.test_results['passed'].append("Crisis detection: crisis text")

        logger.info("\n✓ Crisis detection tests PASSED")
        return True

    async def test_nlp_full_analysis(self):
        """Test complete journal analysis"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Full Journal Analysis")
        logger.info("=" * 80)

        text = "Today was challenging but I managed to push through. Had some anxiety in the morning but felt better after talking to a friend. Overall feeling hopeful about tomorrow."

        try:
            result = await self.nlp_service.analyze_journal_entry(text)

            logger.info(f"\nText: {text}")
            logger.info(f"\nSentiment: {result['sentiment']['label']} ({result['sentiment']['score']:.2f})")
            logger.info(f"Primary emotion: {result['emotions']['primary_emotion']} ({result['emotions']['primary_score']:.2f})")
            logger.info(f"Crisis detected: {result['crisis_detection']['crisis_detected']}")
            logger.info(f"Risk level: {result['crisis_detection']['risk_level']}")
            logger.info(f"Text stats: {result['word_count']} words, {result['text_length']} chars")

            # Validate structure
            assert 'sentiment' in result
            assert 'emotions' in result
            assert 'crisis_detection' in result
            assert 'themes' in result
            assert 'analyzed_at' in result

            self.test_results['passed'].append("Full journal analysis")
            logger.info("\n✓ Full analysis test PASSED")
            return True

        except Exception as e:
            logger.error(f"✗ Full analysis failed: {e}")
            self.test_results['failed'].append(f"Full analysis - {e}")
            import traceback
            traceback.print_exc()
            return False

    # ========================================================================
    # PREDICTION TESTS
    # ========================================================================

    async def test_lstm_model_building(self):
        """Test LSTM model building"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: LSTM Model Building")
        logger.info("=" * 80)

        try:
            model = self.prediction_service.build_lstm_model(
                sequence_length=14,
                n_features=5
            )

            logger.info(f"✓ LSTM model built successfully")
            logger.info(f"  Input shape: {model.input_shape}")
            logger.info(f"  Output shape: {model.output_shape}")
            logger.info(f"  Total parameters: {model.count_params():,}")

            self.test_results['passed'].append("LSTM model building")
            return True

        except Exception as e:
            logger.error(f"✗ LSTM building failed: {e}")
            self.test_results['failed'].append(f"LSTM building - {e}")
            return False

    async def test_lstm_training(self):
        """Test LSTM training"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: LSTM Training")
        logger.info("=" * 80)

        try:
            # Generate training data
            mood_data = self.generate_mood_data(days=60)
            logger.info(f"Generated {len(mood_data)} days of mood data")

            # Train model (few epochs for testing)
            result = await self.prediction_service.train_lstm_model(
                mood_data,
                sequence_length=14,
                epochs=5
            )

            if result['success']:
                logger.info(f"✓ LSTM training completed")
                logger.info(f"  Final loss: {result['final_loss']:.4f}")
                logger.info(f"  Validation loss: {result['final_val_loss']:.4f}")
                logger.info(f"  Epochs trained: {result['epochs_trained']}")

                self.test_results['passed'].append("LSTM training")
                return True
            else:
                logger.error(f"✗ Training failed: {result.get('error')}")
                self.test_results['failed'].append(f"LSTM training - {result.get('error')}")
                return False

        except Exception as e:
            logger.error(f"✗ LSTM training failed: {e}")
            self.test_results['failed'].append(f"LSTM training - {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_mood_prediction(self):
        """Test mood prediction"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Mood Prediction")
        logger.info("=" * 80)

        try:
            # Generate data and train
            mood_data = self.generate_mood_data(days=60)
            await self.prediction_service.train_lstm_model(mood_data, epochs=5)

            # Make predictions
            result = await self.prediction_service.predict_mood(
                mood_data[-14:],
                days_ahead=7,
                include_confidence=True
            )

            if result['success']:
                logger.info(f"✓ Mood predictions generated")
                logger.info(f"\nPredictions for next 7 days:")

                for pred in result['predictions']:
                    logger.info(f"  {pred['date'][:10]}: {pred['predicted_mood']:.2f} "
                              f"(confidence: {pred.get('confidence_lower', 0):.2f} - {pred.get('confidence_upper', 0):.2f})")

                assert len(result['predictions']) == 7, "Wrong number of predictions"
                self.test_results['passed'].append("Mood prediction")
                return True
            else:
                logger.error(f"✗ Prediction failed: {result.get('error')}")
                self.test_results['failed'].append(f"Mood prediction - {result.get('error')}")
                return False

        except Exception as e:
            logger.error(f"✗ Prediction failed: {e}")
            self.test_results['failed'].append(f"Mood prediction - {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_seasonal_patterns(self):
        """Test seasonal pattern detection"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Seasonal Pattern Detection")
        logger.info("=" * 80)

        try:
            mood_data = self.generate_mood_data(days=90)

            result = await self.prediction_service.detect_seasonal_patterns(mood_data)

            if result['patterns_detected']:
                logger.info(f"✓ Patterns detected")

                if 'weekly_pattern' in result:
                    wp = result['weekly_pattern']
                    logger.info(f"\nWeekly pattern:")
                    logger.info(f"  Best day: {wp['best_day']}")
                    logger.info(f"  Worst day: {wp['worst_day']}")
                    logger.info(f"  Pattern detected: {wp['pattern_detected']}")

                if 'monthly_pattern' in result:
                    mp = result['monthly_pattern']
                    logger.info(f"\nMonthly pattern:")
                    logger.info(f"  Beginning: {mp['beginning_of_month']:.2f}")
                    logger.info(f"  Middle: {mp['middle_of_month']:.2f}")
                    logger.info(f"  End: {mp['end_of_month']:.2f}")

                self.test_results['passed'].append("Seasonal patterns")
                return True
            else:
                logger.warning(f"⚠ No patterns detected (may need more data)")
                self.test_results['warnings'].append("Seasonal patterns - no patterns detected")
                return True

        except Exception as e:
            logger.error(f"✗ Pattern detection failed: {e}")
            self.test_results['failed'].append(f"Seasonal patterns - {e}")
            return False

    async def test_sleep_correlation(self):
        """Test sleep-mood correlation"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Sleep Correlation Analysis")
        logger.info("=" * 80)

        try:
            mood_data = self.generate_mood_data(days=30)
            sleep_data = self.generate_sleep_data(days=30)

            result = await self.prediction_service.analyze_sleep_patterns(
                mood_data,
                sleep_data
            )

            if result['sufficient_data']:
                logger.info(f"✓ Sleep correlation analyzed")

                corr = result['sleep_duration_correlation']
                logger.info(f"\nSleep duration correlation:")
                logger.info(f"  Correlation: {corr['correlation']:.3f}")
                logger.info(f"  P-value: {corr['p_value']:.4f}")
                logger.info(f"  Significant: {corr['significant']}")

                optimal = result['optimal_sleep_range']
                logger.info(f"\nOptimal sleep:")
                logger.info(f"  Hours: {optimal['optimal_hours']:.1f}")
                logger.info(f"  Range: {optimal['range']}")

                logger.info(f"\nRecommendation: {result['recommendation']}")

                self.test_results['passed'].append("Sleep correlation")
                return True
            else:
                logger.warning(f"⚠ Insufficient data: {result.get('note')}")
                self.test_results['warnings'].append("Sleep correlation - insufficient data")
                return True

        except Exception as e:
            logger.error(f"✗ Sleep correlation failed: {e}")
            self.test_results['failed'].append(f"Sleep correlation - {e}")
            import traceback
            traceback.print_exc()
            return False

    # ========================================================================
    # COLLABORATIVE FILTERING TESTS
    # ========================================================================

    async def test_user_profile_creation(self):
        """Test user profile creation"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: User Profile Creation")
        logger.info("=" * 80)

        try:
            mood_data = self.generate_mood_data(days=60)

            result = await self.cf_service.create_user_profile(
                "test_user_123",
                mood_data,
                anonymize=True
            )

            if result['success']:
                logger.info(f"✓ User profile created")
                logger.info(f"  Profile ID: {result['profile_id']}")
                logger.info(f"  Features extracted: {len(result['features'])}")
                logger.info(f"  Sample features:")

                for key, value in list(result['features'].items())[:5]:
                    logger.info(f"    {key}: {value:.3f}")

                self.test_results['passed'].append("User profile creation")
                return True
            else:
                logger.error(f"✗ Profile creation failed: {result.get('error')}")
                self.test_results['failed'].append(f"User profile - {result.get('error')}")
                return False

        except Exception as e:
            logger.error(f"✗ Profile creation failed: {e}")
            self.test_results['failed'].append(f"User profile - {e}")
            return False

    async def test_user_clustering(self):
        """Test user clustering"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: User Clustering")
        logger.info("=" * 80)

        try:
            # Create multiple user profiles
            patterns = ['normal', 'improving', 'declining', 'volatile']

            for i in range(12):
                pattern = patterns[i % len(patterns)]
                mood_data = self.generate_mood_data(days=60, user_pattern=pattern)
                await self.cf_service.create_user_profile(
                    f"test_user_{i}",
                    mood_data,
                    anonymize=True
                )

            logger.info(f"Created 12 user profiles")

            # Cluster users
            result = await self.cf_service.cluster_users(
                n_clusters=4,
                method='kmeans'
            )

            if result['success']:
                logger.info(f"✓ Users clustered")
                logger.info(f"  Total users: {result['n_users']}")
                logger.info(f"  Clusters formed: {result['n_clusters']}")
                logger.info(f"  Distribution: {result['cluster_distribution']}")

                logger.info(f"\nCluster analysis:")
                for cluster_id, analysis in result['cluster_analysis'].items():
                    logger.info(f"  Cluster {cluster_id}: {analysis['size']} users")
                    logger.info(f"    {analysis['description']}")

                self.test_results['passed'].append("User clustering")
                return True
            else:
                logger.error(f"✗ Clustering failed: {result.get('error')}")
                self.test_results['failed'].append(f"User clustering - {result.get('error')}")
                return False

        except Exception as e:
            logger.error(f"✗ Clustering failed: {e}")
            self.test_results['failed'].append(f"User clustering - {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_intervention_recommendations(self):
        """Test intervention recommendations"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: Intervention Recommendations")
        logger.info("=" * 80)

        try:
            interventions = [
                {'id': 'meditation_1', 'name': 'Guided Meditation', 'description': '10-min mindfulness', 'category': 'mindfulness'},
                {'id': 'exercise_1', 'name': 'Morning Walk', 'description': '30-min outdoor walk', 'category': 'physical'},
                {'id': 'journaling_1', 'name': 'Gratitude Journal', 'description': 'List 3 things', 'category': 'reflection'},
                {'id': 'breathing_1', 'name': 'Deep Breathing', 'description': '5-min breathing', 'category': 'relaxation'},
                {'id': 'social_1', 'name': 'Call a Friend', 'description': 'Connect with someone', 'category': 'social'}
            ]

            result = await self.cf_service.recommend_interventions(
                "test_user_0",
                interventions,
                n_recommendations=3
            )

            if 'recommendations' in result:
                logger.info(f"✓ Recommendations generated")
                logger.info(f"\nTop recommendations:")

                for i, rec in enumerate(result['recommendations'][:3], 1):
                    logger.info(f"  {i}. {rec['intervention']['name']}")
                    logger.info(f"     Score: {rec['score']:.3f}")
                    logger.info(f"     Confidence: {rec['confidence']:.3f}")
                    if 'note' in rec:
                        logger.info(f"     Note: {rec['note']}")

                self.test_results['passed'].append("Intervention recommendations")
                return True
            else:
                logger.error(f"✗ Recommendations failed")
                self.test_results['failed'].append("Intervention recommendations")
                return False

        except Exception as e:
            logger.error(f"✗ Recommendations failed: {e}")
            self.test_results['failed'].append(f"Intervention recommendations - {e}")
            return False

    async def test_ab_testing(self):
        """Test A/B testing framework"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST: A/B Testing")
        logger.info("=" * 80)

        try:
            # Create test
            variants = [
                {'id': 'control', 'name': 'Standard Meditation'},
                {'id': 'treatment', 'name': 'Enhanced Meditation'}
            ]

            result = await self.cf_service.create_ab_test(
                "meditation_comparison",
                variants,
                "mood_improvement",
                duration_days=30
            )

            if result['success']:
                test_id = result['test_id']
                logger.info(f"✓ A/B test created: {test_id}")

                # Assign users and record results
                for i in range(20):
                    # Assign to variant
                    assignment = await self.cf_service.assign_user_to_variant(
                        test_id,
                        f"test_user_{i}",
                        method='balanced'
                    )

                    # Simulate result
                    if assignment['success']:
                        variant = assignment['variant']
                        # Treatment has slightly better results
                        if variant == 'treatment':
                            metric = np.random.normal(7.5, 1)
                        else:
                            metric = np.random.normal(6.5, 1)

                        await self.cf_service.record_ab_test_result(
                            test_id,
                            f"test_user_{i}",
                            metric
                        )

                logger.info(f"  Assigned 20 users and recorded results")

                # Analyze
                analysis = await self.cf_service.analyze_ab_test(test_id)

                if analysis['success']:
                    logger.info(f"\n  Analysis:")
                    for variant_id, stats in analysis['results'].items():
                        logger.info(f"    {variant_id}: n={stats['n']}, mean={stats['mean']:.2f}, std={stats['std']:.2f}")

                    if analysis.get('statistical_test'):
                        st = analysis['statistical_test']
                        logger.info(f"\n  Statistical test:")
                        logger.info(f"    p-value: {st['p_value']:.4f}")
                        logger.info(f"    Significant: {st['significant']}")
                        logger.info(f"    Winner: {st['winner']}")

                    logger.info(f"\n  Recommendation: {analysis['recommendation']}")

                    self.test_results['passed'].append("A/B testing")
                    return True

        except Exception as e:
            logger.error(f"✗ A/B testing failed: {e}")
            self.test_results['failed'].append(f"A/B testing - {e}")
            import traceback
            traceback.print_exc()
            return False

    # ========================================================================
    # MAIN TEST RUNNER
    # ========================================================================

    async def run_all_tests(self):
        """Run all tests"""
        logger.info("\n" + "=" * 80)
        logger.info("FIREFLY ML COMPREHENSIVE TEST SUITE")
        logger.info("=" * 80)

        # Initialize services
        if not await self.setup_services():
            logger.error("Failed to initialize services. Exiting.")
            return False

        # Run tests
        tests = [
            ("NLP: Sentiment Analysis", self.test_nlp_sentiment_analysis),
            ("NLP: Emotion Classification", self.test_nlp_emotion_classification),
            ("NLP: Crisis Detection", self.test_nlp_crisis_detection),
            ("NLP: Full Analysis", self.test_nlp_full_analysis),
            ("Prediction: LSTM Building", self.test_lstm_model_building),
            ("Prediction: LSTM Training", self.test_lstm_training),
            ("Prediction: Mood Prediction", self.test_mood_prediction),
            ("Prediction: Seasonal Patterns", self.test_seasonal_patterns),
            ("Prediction: Sleep Correlation", self.test_sleep_correlation),
            ("CF: User Profile Creation", self.test_user_profile_creation),
            ("CF: User Clustering", self.test_user_clustering),
            ("CF: Intervention Recommendations", self.test_intervention_recommendations),
            ("CF: A/B Testing", self.test_ab_testing),
        ]

        for test_name, test_func in tests:
            try:
                await test_func()
                await asyncio.sleep(0.5)  # Small delay between tests
            except Exception as e:
                logger.error(f"Test '{test_name}' crashed: {e}")
                self.test_results['failed'].append(f"{test_name} - crashed: {e}")

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)

        total = len(self.test_results['passed']) + len(self.test_results['failed'])
        passed = len(self.test_results['passed'])
        failed = len(self.test_results['failed'])
        warnings = len(self.test_results['warnings'])

        logger.info(f"\nTotal tests: {total}")
        logger.info(f"✓ Passed: {passed}")
        logger.info(f"✗ Failed: {failed}")
        logger.info(f"⚠ Warnings: {warnings}")

        if failed > 0:
            logger.info("\nFailed tests:")
            for test in self.test_results['failed']:
                logger.info(f"  ✗ {test}")

        if warnings > 0:
            logger.info("\nWarnings:")
            for warning in self.test_results['warnings']:
                logger.info(f"  ⚠ {warning}")

        success_rate = (passed / total * 100) if total > 0 else 0
        logger.info(f"\nSuccess rate: {success_rate:.1f}%")

        if failed == 0:
            logger.info("\n" + "=" * 80)
            logger.info("🎉 ALL TESTS PASSED! ML SYSTEM IS OPERATIONAL!")
            logger.info("=" * 80)
        else:
            logger.info("\n" + "=" * 80)
            logger.info("❌ SOME TESTS FAILED. PLEASE REVIEW ERRORS ABOVE.")
            logger.info("=" * 80)


async def main():
    """Main entry point"""
    tester = MLTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
