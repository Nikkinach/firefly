"""
Collaborative Filtering Service
Implements user clustering, intervention recommendations, and A/B testing framework
"""

import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import hashlib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from scipy.spatial.distance import euclidean

logger = logging.getLogger(__name__)


class CollaborativeFilteringService:
    """
    Collaborative filtering for personalized recommendations
    Privacy-preserving user clustering and intervention recommendations
    """

    def __init__(self):
        """Initialize collaborative filtering service"""
        self.user_clusters = {}
        self.cluster_model = None
        self.scaler = StandardScaler()
        self.user_profiles = {}
        self.intervention_effectiveness = {}
        self.ab_tests = {}

    async def create_user_profile(
        self,
        user_id: str,
        mood_data: List[Dict],
        demographics: Optional[Dict] = None,
        anonymize: bool = True
    ) -> Dict:
        """
        Create anonymized user profile for clustering

        Args:
            user_id: User identifier
            mood_data: Historical mood data
            demographics: Optional demographic information
            anonymize: Whether to anonymize the user ID

        Returns:
            User profile features
        """
        try:
            # Anonymize user ID
            if anonymize:
                profile_id = self._anonymize_user_id(user_id)
            else:
                profile_id = user_id

            # Extract features from mood data
            features = self._extract_user_features(mood_data)

            # Add demographic features if provided (anonymized)
            if demographics:
                demo_features = self._extract_demographic_features(demographics)
                features.update(demo_features)

            # Store profile
            self.user_profiles[profile_id] = {
                'features': features,
                'created_at': datetime.utcnow().isoformat(),
                'n_data_points': len(mood_data)
            }

            return {
                'profile_id': profile_id,
                'features': features,
                'success': True
            }

        except Exception as e:
            logger.error(f"User profile creation error: {e}")
            return {'success': False, 'error': str(e)}

    def _anonymize_user_id(self, user_id: str) -> str:
        """Create anonymized hash of user ID"""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]

    def _extract_user_features(self, mood_data: List[Dict]) -> Dict:
        """
        Extract feature vector from user's mood data

        Args:
            mood_data: Historical mood data

        Returns:
            Feature dictionary
        """
        df = pd.DataFrame(mood_data)

        if len(df) == 0:
            return self._default_features()

        # Statistical features
        features = {
            # Central tendency
            'mean_mood': float(df['mood_score'].mean()),
            'median_mood': float(df['mood_score'].median()),

            # Variability
            'std_mood': float(df['mood_score'].std()),
            'mood_range': float(df['mood_score'].max() - df['mood_score'].min()),
            'coefficient_of_variation': float(df['mood_score'].std() / df['mood_score'].mean())
            if df['mood_score'].mean() > 0 else 0,

            # Trends
            'trend': self._calculate_trend(df['mood_score'].values),
            'positive_days_ratio': float((df['mood_score'] >= 7).sum() / len(df)),
            'negative_days_ratio': float((df['mood_score'] <= 4).sum() / len(df)),

            # Volatility
            'daily_change_mean': float(df['mood_score'].diff().abs().mean()),
            'daily_change_std': float(df['mood_score'].diff().std()),

            # Temporal patterns
            'weekend_effect': self._calculate_weekend_effect(df),
            'consistency_score': self._calculate_consistency_score(df)
        }

        return features

    def _calculate_trend(self, values: np.ndarray) -> float:
        """Calculate linear trend of mood over time"""
        if len(values) < 2:
            return 0.0

        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, 1)
        return float(coeffs[0])  # Slope

    def _calculate_weekend_effect(self, df: pd.DataFrame) -> float:
        """Calculate difference between weekend and weekday mood"""
        if 'date' not in df.columns:
            return 0.0

        df['date'] = pd.to_datetime(df['date'])
        df['is_weekend'] = df['date'].dt.dayofweek >= 5

        if df['is_weekend'].sum() == 0 or (~df['is_weekend']).sum() == 0:
            return 0.0

        weekend_mood = df[df['is_weekend']]['mood_score'].mean()
        weekday_mood = df[~df['is_weekend']]['mood_score'].mean()

        return float(weekend_mood - weekday_mood)

    def _calculate_consistency_score(self, df: pd.DataFrame) -> float:
        """Calculate how consistent mood patterns are"""
        if len(df) < 7:
            return 0.0

        # Calculate autocorrelation
        mood_values = df['mood_score'].values
        mean = np.mean(mood_values)
        var = np.var(mood_values)

        if var == 0:
            return 1.0

        # Lag-1 autocorrelation
        autocorr = np.correlate(
            mood_values[:-1] - mean,
            mood_values[1:] - mean,
            mode='valid'
        )[0] / (var * (len(mood_values) - 1))

        return float(autocorr)

    def _extract_demographic_features(self, demographics: Dict) -> Dict:
        """Extract and anonymize demographic features"""
        features = {}

        # Age group (binned for privacy)
        if 'age' in demographics:
            age = demographics['age']
            age_group = (age // 10) * 10  # Round to decade
            features['age_group'] = age_group

        # Other anonymized features
        if 'timezone_offset' in demographics:
            features['timezone_offset'] = demographics['timezone_offset']

        return features

    def _default_features(self) -> Dict:
        """Return default feature values"""
        return {
            'mean_mood': 5.0,
            'median_mood': 5.0,
            'std_mood': 0.0,
            'mood_range': 0.0,
            'coefficient_of_variation': 0.0,
            'trend': 0.0,
            'positive_days_ratio': 0.0,
            'negative_days_ratio': 0.0,
            'daily_change_mean': 0.0,
            'daily_change_std': 0.0,
            'weekend_effect': 0.0,
            'consistency_score': 0.0
        }

    async def cluster_users(
        self,
        n_clusters: int = 5,
        method: str = 'kmeans'
    ) -> Dict:
        """
        Cluster users based on their profiles

        Args:
            n_clusters: Number of clusters (for KMeans)
            method: Clustering method ('kmeans' or 'dbscan')

        Returns:
            Clustering results
        """
        try:
            if len(self.user_profiles) < n_clusters:
                return {
                    'success': False,
                    'error': f'Need at least {n_clusters} user profiles'
                }

            # Prepare feature matrix
            profile_ids = list(self.user_profiles.keys())
            features = [
                list(self.user_profiles[pid]['features'].values())
                for pid in profile_ids
            ]

            X = np.array(features)

            # Standardize features
            X_scaled = self.scaler.fit_transform(X)

            # Apply clustering
            if method == 'kmeans':
                self.cluster_model = KMeans(
                    n_clusters=n_clusters,
                    random_state=42,
                    n_init=10
                )
            elif method == 'dbscan':
                self.cluster_model = DBSCAN(
                    eps=0.5,
                    min_samples=3
                )
            else:
                return {'success': False, 'error': f'Unknown method: {method}'}

            cluster_labels = self.cluster_model.fit_predict(X_scaled)

            # Store cluster assignments
            for pid, label in zip(profile_ids, cluster_labels):
                self.user_clusters[pid] = int(label)

            # Analyze clusters
            cluster_analysis = self._analyze_clusters(
                X_scaled,
                cluster_labels,
                profile_ids
            )

            return {
                'success': True,
                'n_users': len(profile_ids),
                'n_clusters': len(set(cluster_labels)),
                'cluster_distribution': dict(pd.Series(cluster_labels).value_counts()),
                'cluster_analysis': cluster_analysis
            }

        except Exception as e:
            logger.error(f"User clustering error: {e}")
            return {'success': False, 'error': str(e)}

    def _analyze_clusters(
        self,
        X: np.ndarray,
        labels: np.ndarray,
        profile_ids: List[str]
    ) -> Dict:
        """Analyze cluster characteristics"""
        clusters = {}

        for cluster_id in set(labels):
            if cluster_id == -1:  # Noise cluster in DBSCAN
                continue

            cluster_mask = labels == cluster_id
            cluster_data = X[cluster_mask]

            # Get original feature names
            sample_profile = list(self.user_profiles.values())[0]
            feature_names = list(sample_profile['features'].keys())

            # Calculate cluster center (in original feature space)
            cluster_center = cluster_data.mean(axis=0)

            # Find defining features (highest deviation from global mean)
            global_mean = X.mean(axis=0)
            feature_importance = np.abs(cluster_center - global_mean)
            top_features_idx = np.argsort(feature_importance)[-3:][::-1]

            clusters[int(cluster_id)] = {
                'size': int(cluster_mask.sum()),
                'defining_features': [
                    {
                        'feature': feature_names[idx],
                        'value': float(cluster_center[idx])
                    }
                    for idx in top_features_idx
                ],
                'description': self._generate_cluster_description(
                    cluster_id,
                    feature_names,
                    cluster_center
                )
            }

        return clusters

    def _generate_cluster_description(
        self,
        cluster_id: int,
        feature_names: List[str],
        center: np.ndarray
    ) -> str:
        """Generate human-readable cluster description"""
        # Simple heuristic based on mean mood
        mean_mood_idx = feature_names.index('mean_mood') if 'mean_mood' in feature_names else 0
        mean_mood = center[mean_mood_idx]

        if mean_mood < 4:
            return f"Cluster {cluster_id}: Users experiencing low mood consistently"
        elif mean_mood > 7:
            return f"Cluster {cluster_id}: Users with generally high mood"
        else:
            return f"Cluster {cluster_id}: Users with moderate mood patterns"

    async def find_similar_users(
        self,
        user_id: str,
        top_k: int = 10
    ) -> Dict:
        """
        Find similar users based on profile similarity

        Args:
            user_id: Target user ID
            top_k: Number of similar users to return

        Returns:
            List of similar users (anonymized)
        """
        try:
            profile_id = self._anonymize_user_id(user_id)

            if profile_id not in self.user_profiles:
                return {'success': False, 'error': 'User profile not found'}

            # Get user's feature vector
            user_features = np.array(
                list(self.user_profiles[profile_id]['features'].values())
            ).reshape(1, -1)

            # Get all other users' features
            other_profiles = {
                pid: prof for pid, prof in self.user_profiles.items()
                if pid != profile_id
            }

            if len(other_profiles) == 0:
                return {'success': False, 'error': 'No other users to compare'}

            other_ids = list(other_profiles.keys())
            other_features = np.array([
                list(other_profiles[pid]['features'].values())
                for pid in other_ids
            ])

            # Calculate similarities
            similarities = cosine_similarity(user_features, other_features)[0]

            # Get top-k similar users
            top_indices = np.argsort(similarities)[-top_k:][::-1]

            similar_users = [
                {
                    'profile_id': other_ids[idx],
                    'similarity': float(similarities[idx]),
                    'cluster': self.user_clusters.get(other_ids[idx])
                }
                for idx in top_indices
            ]

            return {
                'success': True,
                'user_cluster': self.user_clusters.get(profile_id),
                'similar_users': similar_users
            }

        except Exception as e:
            logger.error(f"Similar users search error: {e}")
            return {'success': False, 'error': str(e)}

    async def recommend_interventions(
        self,
        user_id: str,
        available_interventions: List[Dict],
        n_recommendations: int = 5
    ) -> Dict:
        """
        Recommend interventions based on similar users' success

        Args:
            user_id: User ID
            available_interventions: List of available interventions
            n_recommendations: Number of recommendations

        Returns:
            Ranked intervention recommendations
        """
        try:
            # Find similar users
            similar_users = await self.find_similar_users(user_id, top_k=20)

            if not similar_users.get('success'):
                # Fallback to general recommendations
                return self._get_general_recommendations(
                    available_interventions,
                    n_recommendations
                )

            # Get interventions that worked for similar users
            intervention_scores = {}

            for similar_user in similar_users['similar_users']:
                similarity = similar_user['similarity']
                profile_id = similar_user['profile_id']

                # Get effective interventions for this user
                if profile_id in self.intervention_effectiveness:
                    for intervention_id, effectiveness in \
                            self.intervention_effectiveness[profile_id].items():
                        if intervention_id not in intervention_scores:
                            intervention_scores[intervention_id] = {
                                'weighted_effectiveness': 0,
                                'total_weight': 0,
                                'n_users': 0
                            }

                        intervention_scores[intervention_id]['weighted_effectiveness'] += \
                            effectiveness * similarity
                        intervention_scores[intervention_id]['total_weight'] += similarity
                        intervention_scores[intervention_id]['n_users'] += 1

            # Calculate final scores
            recommendations = []
            for intervention in available_interventions:
                intervention_id = intervention['id']

                if intervention_id in intervention_scores:
                    score_data = intervention_scores[intervention_id]
                    avg_effectiveness = (
                        score_data['weighted_effectiveness'] /
                        score_data['total_weight']
                        if score_data['total_weight'] > 0 else 0
                    )

                    recommendations.append({
                        'intervention': intervention,
                        'score': avg_effectiveness,
                        'evidence_from_n_users': score_data['n_users'],
                        'confidence': min(score_data['n_users'] / 5, 1.0)
                    })

            # Sort by score
            recommendations.sort(key=lambda x: x['score'], reverse=True)

            # Fill with general recommendations if needed
            if len(recommendations) < n_recommendations:
                general = self._get_general_recommendations(
                    available_interventions,
                    n_recommendations - len(recommendations)
                )
                recommendations.extend(general['recommendations'])

            return {
                'success': True,
                'recommendations': recommendations[:n_recommendations],
                'based_on_similar_users': len(similar_users.get('similar_users', []))
            }

        except Exception as e:
            logger.error(f"Intervention recommendation error: {e}")
            return {'success': False, 'error': str(e)}

    def _get_general_recommendations(
        self,
        interventions: List[Dict],
        n: int
    ) -> Dict:
        """Get general recommendations when no user data available"""
        # Simple popularity-based ranking
        recommendations = [
            {
                'intervention': intervention,
                'score': 0.5,  # Neutral score
                'evidence_from_n_users': 0,
                'confidence': 0.3,  # Low confidence
                'note': 'General recommendation (no personalization data)'
            }
            for intervention in interventions[:n]
        ]

        return {'recommendations': recommendations}

    async def record_intervention_effectiveness(
        self,
        user_id: str,
        intervention_id: str,
        effectiveness_score: float
    ) -> Dict:
        """
        Record how effective an intervention was for a user

        Args:
            user_id: User ID
            intervention_id: Intervention ID
            effectiveness_score: Score from 0 to 1

        Returns:
            Success status
        """
        try:
            profile_id = self._anonymize_user_id(user_id)

            if profile_id not in self.intervention_effectiveness:
                self.intervention_effectiveness[profile_id] = {}

            self.intervention_effectiveness[profile_id][intervention_id] = \
                float(effectiveness_score)

            return {'success': True}

        except Exception as e:
            logger.error(f"Recording intervention effectiveness error: {e}")
            return {'success': False, 'error': str(e)}

    async def create_ab_test(
        self,
        test_name: str,
        variants: List[Dict],
        target_metric: str,
        duration_days: int = 30
    ) -> Dict:
        """
        Create A/B test for new interventions

        Args:
            test_name: Name of the test
            variants: List of variants to test
            target_metric: Metric to optimize
            duration_days: Test duration

        Returns:
            A/B test configuration
        """
        try:
            test_id = hashlib.sha256(
                f"{test_name}_{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16]

            test_config = {
                'test_id': test_id,
                'name': test_name,
                'variants': variants,
                'target_metric': target_metric,
                'start_date': datetime.utcnow().isoformat(),
                'end_date': (datetime.utcnow() + timedelta(days=duration_days)).isoformat(),
                'status': 'active',
                'assignments': {},  # user_id -> variant_id
                'results': {v['id']: [] for v in variants}
            }

            self.ab_tests[test_id] = test_config

            return {
                'success': True,
                'test_id': test_id,
                'config': test_config
            }

        except Exception as e:
            logger.error(f"A/B test creation error: {e}")
            return {'success': False, 'error': str(e)}

    async def assign_user_to_variant(
        self,
        test_id: str,
        user_id: str,
        method: str = 'random'
    ) -> Dict:
        """
        Assign user to A/B test variant

        Args:
            test_id: Test ID
            user_id: User ID
            method: Assignment method ('random' or 'balanced')

        Returns:
            Assigned variant
        """
        try:
            if test_id not in self.ab_tests:
                return {'success': False, 'error': 'Test not found'}

            test = self.ab_tests[test_id]

            # Check if already assigned
            profile_id = self._anonymize_user_id(user_id)
            if profile_id in test['assignments']:
                assigned_variant = test['assignments'][profile_id]
                return {
                    'success': True,
                    'variant': assigned_variant,
                    'new_assignment': False
                }

            # Assign to variant
            if method == 'random':
                # Random assignment
                variant_id = np.random.choice([v['id'] for v in test['variants']])
            elif method == 'balanced':
                # Balanced assignment (minimize difference in group sizes)
                variant_counts = {v['id']: 0 for v in test['variants']}
                for assigned in test['assignments'].values():
                    variant_counts[assigned] += 1

                variant_id = min(variant_counts.items(), key=lambda x: x[1])[0]
            else:
                return {'success': False, 'error': f'Unknown method: {method}'}

            # Record assignment
            test['assignments'][profile_id] = variant_id

            return {
                'success': True,
                'variant': variant_id,
                'new_assignment': True
            }

        except Exception as e:
            logger.error(f"Variant assignment error: {e}")
            return {'success': False, 'error': str(e)}

    async def record_ab_test_result(
        self,
        test_id: str,
        user_id: str,
        metric_value: float
    ) -> Dict:
        """
        Record A/B test result for a user

        Args:
            test_id: Test ID
            user_id: User ID
            metric_value: Measured metric value

        Returns:
            Success status
        """
        try:
            if test_id not in self.ab_tests:
                return {'success': False, 'error': 'Test not found'}

            test = self.ab_tests[test_id]
            profile_id = self._anonymize_user_id(user_id)

            if profile_id not in test['assignments']:
                return {'success': False, 'error': 'User not assigned to test'}

            variant_id = test['assignments'][profile_id]
            test['results'][variant_id].append(float(metric_value))

            return {'success': True}

        except Exception as e:
            logger.error(f"Recording A/B test result error: {e}")
            return {'success': False, 'error': str(e)}

    async def analyze_ab_test(self, test_id: str) -> Dict:
        """
        Analyze A/B test results

        Args:
            test_id: Test ID

        Returns:
            Statistical analysis of test results
        """
        try:
            if test_id not in self.ab_tests:
                return {'success': False, 'error': 'Test not found'}

            test = self.ab_tests[test_id]
            results = {}

            for variant_id, values in test['results'].items():
                if len(values) == 0:
                    continue

                results[variant_id] = {
                    'n': len(values),
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'median': float(np.median(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values))
                }

            # Statistical comparison (if 2 variants)
            variant_ids = list(results.keys())
            if len(variant_ids) == 2:
                from scipy.stats import ttest_ind

                values_a = test['results'][variant_ids[0]]
                values_b = test['results'][variant_ids[1]]

                if len(values_a) > 1 and len(values_b) > 1:
                    t_stat, p_value = ttest_ind(values_a, values_b)

                    statistical_test = {
                        'test': 't-test',
                        't_statistic': float(t_stat),
                        'p_value': float(p_value),
                        'significant': p_value < 0.05,
                        'winner': variant_ids[0] if results[variant_ids[0]]['mean'] >
                                  results[variant_ids[1]]['mean'] else variant_ids[1]
                    }
                else:
                    statistical_test = None
            else:
                statistical_test = None

            return {
                'success': True,
                'test_id': test_id,
                'test_name': test['name'],
                'results': results,
                'statistical_test': statistical_test,
                'recommendation': self._generate_ab_test_recommendation(
                    results,
                    statistical_test
                )
            }

        except Exception as e:
            logger.error(f"A/B test analysis error: {e}")
            return {'success': False, 'error': str(e)}

    def _generate_ab_test_recommendation(
        self,
        results: Dict,
        statistical_test: Optional[Dict]
    ) -> str:
        """Generate recommendation based on A/B test results"""
        if not results:
            return "Insufficient data to make recommendation"

        if statistical_test and statistical_test['significant']:
            winner = statistical_test['winner']
            return f"Variant {winner} shows statistically significant improvement (p < 0.05)"

        best_variant = max(results.items(), key=lambda x: x[1]['mean'])
        return f"Variant {best_variant[0]} shows best performance, but results not statistically significant yet"


# Singleton instance
_collaborative_filtering_instance = None


def get_collaborative_filtering_service() -> CollaborativeFilteringService:
    """Get or create collaborative filtering service singleton"""
    global _collaborative_filtering_instance
    if _collaborative_filtering_instance is None:
        _collaborative_filtering_instance = CollaborativeFilteringService()
    return _collaborative_filtering_instance
