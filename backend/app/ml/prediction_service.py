"""
Advanced Prediction Service for Mood Forecasting
Implements LSTM/Transformer models, seasonal pattern detection, weather correlation, and sleep analysis
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from scipy import stats
from scipy.fft import fft
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import torch
from transformers import TimeSeriesTransformerForPrediction, TimeSeriesTransformerConfig

logger = logging.getLogger(__name__)


class PredictionService:
    """Advanced prediction service for mood forecasting and pattern analysis"""

    def __init__(self):
        """Initialize prediction models"""
        self.lstm_model = None
        self.transformer_model = None
        self.scaler = MinMaxScaler()
        self.is_lstm_trained = False
        self.is_transformer_trained = False

    def build_lstm_model(self, sequence_length: int = 14, n_features: int = 5) -> keras.Model:
        """
        Build LSTM model for mood forecasting

        Args:
            sequence_length: Number of past days to consider
            n_features: Number of input features

        Returns:
            Compiled LSTM model
        """
        model = keras.Sequential([
            # First LSTM layer with return sequences
            layers.LSTM(
                128,
                return_sequences=True,
                input_shape=(sequence_length, n_features),
                dropout=0.2,
                recurrent_dropout=0.2
            ),
            layers.BatchNormalization(),

            # Second LSTM layer
            layers.LSTM(
                64,
                return_sequences=True,
                dropout=0.2,
                recurrent_dropout=0.2
            ),
            layers.BatchNormalization(),

            # Third LSTM layer
            layers.LSTM(
                32,
                return_sequences=False,
                dropout=0.2
            ),
            layers.BatchNormalization(),

            # Dense layers for prediction
            layers.Dense(16, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(8, activation='relu'),

            # Output layer - predicts mood score (0-10) for next 7 days
            layers.Dense(7, activation='linear')
        ])

        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae', 'mse']
        )

        logger.info(f"LSTM model built: {model.count_params()} parameters")
        return model

    def build_transformer_model(self, sequence_length: int = 30) -> TimeSeriesTransformerForPrediction:
        """
        Build Transformer model for mood forecasting

        Args:
            sequence_length: Context length for prediction

        Returns:
            Transformer model
        """
        config = TimeSeriesTransformerConfig(
            prediction_length=7,  # Predict 7 days ahead
            context_length=sequence_length,
            distribution_output="normal",
            input_size=1,
            lags_sequence=[1, 2, 3, 7, 14, 30],
            num_time_features=4,  # day of week, day of month, month, day of year
            num_static_categorical_features=0,
            num_static_real_features=0,
            cardinality=[],
            embedding_dimension=[],
            encoder_layers=4,
            decoder_layers=4,
            d_model=64,
            encoder_attention_heads=4,
            decoder_attention_heads=4,
            encoder_ffn_dim=256,
            decoder_ffn_dim=256,
            dropout=0.1,
        )

        model = TimeSeriesTransformerForPrediction(config)
        logger.info("Transformer model built for time series prediction")
        return model

    async def train_lstm_model(
        self,
        mood_data: List[Dict],
        sequence_length: int = 14,
        epochs: int = 50
    ) -> Dict:
        """
        Train LSTM model on historical mood data

        Args:
            mood_data: List of mood records with dates and scores
            sequence_length: Number of past days to use for prediction
            epochs: Training epochs

        Returns:
            Training results
        """
        try:
            # Prepare data
            df = pd.DataFrame(mood_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            # Create feature matrix
            features = self._prepare_features(df)

            if len(features) < sequence_length + 7:
                return {
                    'success': False,
                    'error': 'Insufficient data for training (need at least 21 days)'
                }

            # Create sequences
            X, y = self._create_sequences(features, sequence_length, prediction_horizon=7)

            # Split train/validation
            split_idx = int(len(X) * 0.8)
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]

            # Build model if not exists
            if self.lstm_model is None:
                self.lstm_model = self.build_lstm_model(
                    sequence_length=sequence_length,
                    n_features=X.shape[2]
                )

            # Train model
            history = self.lstm_model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=epochs,
                batch_size=16,
                callbacks=[
                    keras.callbacks.EarlyStopping(
                        patience=10,
                        restore_best_weights=True
                    ),
                    keras.callbacks.ReduceLROnPlateau(
                        factor=0.5,
                        patience=5
                    )
                ],
                verbose=0
            )

            self.is_lstm_trained = True

            return {
                'success': True,
                'final_loss': float(history.history['loss'][-1]),
                'final_val_loss': float(history.history['val_loss'][-1]),
                'epochs_trained': len(history.history['loss']),
                'model_params': self.lstm_model.count_params()
            }

        except Exception as e:
            logger.error(f"LSTM training error: {e}")
            return {'success': False, 'error': str(e)}

    async def predict_mood(
        self,
        recent_data: List[Dict],
        days_ahead: int = 7,
        include_confidence: bool = True
    ) -> Dict:
        """
        Predict mood for upcoming days

        Args:
            recent_data: Recent mood records
            days_ahead: Number of days to predict
            include_confidence: Include confidence intervals

        Returns:
            Mood predictions with confidence intervals
        """
        if not self.is_lstm_trained or self.lstm_model is None:
            return {
                'success': False,
                'error': 'Model not trained yet'
            }

        try:
            # Prepare features
            df = pd.DataFrame(recent_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            features = self._prepare_features(df)

            # Get last sequence
            sequence_length = self.lstm_model.input_shape[1]
            if len(features) < sequence_length:
                return {
                    'success': False,
                    'error': f'Need at least {sequence_length} days of data'
                }

            X = features[-sequence_length:].reshape(1, sequence_length, -1)

            # Make prediction
            predictions = self.lstm_model.predict(X, verbose=0)[0]

            # Generate prediction dates
            last_date = df['date'].max()
            prediction_dates = [
                (last_date + timedelta(days=i+1)).isoformat()
                for i in range(len(predictions))
            ]

            # Calculate confidence intervals using Monte Carlo dropout
            if include_confidence:
                confidence_intervals = self._calculate_confidence_intervals(
                    X, n_iterations=100
                )
            else:
                confidence_intervals = None

            return {
                'success': True,
                'predictions': [
                    {
                        'date': date,
                        'predicted_mood': float(pred),
                        'confidence_lower': float(confidence_intervals[i][0]) if confidence_intervals else None,
                        'confidence_upper': float(confidence_intervals[i][1]) if confidence_intervals else None
                    }
                    for i, (date, pred) in enumerate(zip(prediction_dates, predictions))
                ],
                'model_type': 'lstm'
            }

        except Exception as e:
            logger.error(f"Mood prediction error: {e}")
            return {'success': False, 'error': str(e)}

    def _prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Prepare feature matrix from mood data

        Args:
            df: DataFrame with mood data

        Returns:
            Feature matrix
        """
        # Extract temporal features
        df['day_of_week'] = df['date'].dt.dayofweek / 6.0  # Normalize to [0, 1]
        df['day_of_month'] = df['date'].dt.day / 31.0
        df['month'] = df['date'].dt.month / 12.0
        df['day_of_year'] = df['date'].dt.dayofyear / 365.0

        # Normalize mood score
        df['mood_normalized'] = df['mood_score'] / 10.0

        # Create feature columns
        feature_columns = [
            'mood_normalized',
            'day_of_week',
            'day_of_month',
            'month',
            'day_of_year'
        ]

        return df[feature_columns].values

    def _create_sequences(
        self,
        data: np.ndarray,
        sequence_length: int,
        prediction_horizon: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM training

        Args:
            data: Feature matrix
            sequence_length: Length of input sequences
            prediction_horizon: Number of days to predict

        Returns:
            X (sequences) and y (targets)
        """
        X, y = [], []

        for i in range(len(data) - sequence_length - prediction_horizon + 1):
            X.append(data[i:i + sequence_length])
            # Target is mood scores for next N days
            y.append(data[i + sequence_length:i + sequence_length + prediction_horizon, 0])

        return np.array(X), np.array(y)

    def _calculate_confidence_intervals(
        self,
        X: np.ndarray,
        n_iterations: int = 100
    ) -> List[Tuple[float, float]]:
        """
        Calculate confidence intervals using Monte Carlo dropout

        Args:
            X: Input sequence
            n_iterations: Number of Monte Carlo iterations

        Returns:
            List of (lower, upper) confidence bounds
        """
        predictions = []

        # Enable dropout at inference time
        for _ in range(n_iterations):
            pred = self.lstm_model(X, training=True)
            predictions.append(pred.numpy()[0])

        predictions = np.array(predictions)

        # Calculate percentiles
        lower = np.percentile(predictions, 2.5, axis=0)
        upper = np.percentile(predictions, 97.5, axis=0)

        return list(zip(lower, upper))

    async def detect_seasonal_patterns(
        self,
        mood_data: List[Dict],
        min_data_points: int = 90
    ) -> Dict:
        """
        Detect seasonal patterns in mood data

        Args:
            mood_data: Historical mood data
            min_data_points: Minimum data points required

        Returns:
            Detected seasonal patterns
        """
        try:
            df = pd.DataFrame(mood_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            if len(df) < min_data_points:
                return {
                    'patterns_detected': False,
                    'note': f'Need at least {min_data_points} days of data'
                }

            # Create time series
            ts = df.set_index('date')['mood_score']

            # Detect weekly patterns
            weekly_pattern = self._detect_weekly_pattern(ts)

            # Detect monthly patterns
            monthly_pattern = self._detect_monthly_pattern(ts)

            # Detect yearly patterns (if enough data)
            yearly_pattern = None
            if len(df) >= 365:
                yearly_pattern = self._detect_yearly_pattern(ts)

            # FFT-based frequency detection
            dominant_frequencies = self._detect_frequencies(ts)

            return {
                'patterns_detected': True,
                'weekly_pattern': weekly_pattern,
                'monthly_pattern': monthly_pattern,
                'yearly_pattern': yearly_pattern,
                'dominant_cycles': dominant_frequencies,
                'data_span_days': len(df)
            }

        except Exception as e:
            logger.error(f"Seasonal pattern detection error: {e}")
            return {'patterns_detected': False, 'error': str(e)}

    def _detect_weekly_pattern(self, ts: pd.Series) -> Dict:
        """Detect weekly patterns"""
        df = ts.to_frame('mood')
        df['day_of_week'] = df.index.dayofweek

        weekly_avg = df.groupby('day_of_week')['mood'].agg(['mean', 'std', 'count'])
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Find best and worst days
        best_day_idx = weekly_avg['mean'].idxmax()
        worst_day_idx = weekly_avg['mean'].idxmin()

        # Statistical test for weekly pattern
        groups = [df[df['day_of_week'] == i]['mood'].values for i in range(7)]
        f_stat, p_value = stats.f_oneway(*groups)

        return {
            'pattern_detected': p_value < 0.05,
            'p_value': float(p_value),
            'best_day': day_names[best_day_idx],
            'worst_day': day_names[worst_day_idx],
            'day_averages': {
                day_names[i]: {
                    'mean': float(weekly_avg.loc[i, 'mean']),
                    'std': float(weekly_avg.loc[i, 'std'])
                }
                for i in range(7)
            }
        }

    def _detect_monthly_pattern(self, ts: pd.Series) -> Dict:
        """Detect monthly patterns"""
        df = ts.to_frame('mood')
        df['day_of_month'] = df.index.day

        # Group by day of month
        monthly_avg = df.groupby('day_of_month')['mood'].agg(['mean', 'std', 'count'])

        # Detect beginning/middle/end of month patterns
        beginning = monthly_avg.loc[1:10, 'mean'].mean()
        middle = monthly_avg.loc[11:20, 'mean'].mean()
        end = monthly_avg.loc[21:31, 'mean'].mean()

        return {
            'beginning_of_month': float(beginning),
            'middle_of_month': float(middle),
            'end_of_month': float(end),
            'pattern': 'beginning' if beginning == max(beginning, middle, end) else
                      'middle' if middle == max(beginning, middle, end) else 'end'
        }

    def _detect_yearly_pattern(self, ts: pd.Series) -> Dict:
        """Detect yearly/seasonal patterns"""
        df = ts.to_frame('mood')
        df['month'] = df.index.month

        monthly_avg = df.groupby('month')['mood'].agg(['mean', 'std', 'count'])
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]

        best_month_idx = monthly_avg['mean'].idxmax()
        worst_month_idx = monthly_avg['mean'].idxmin()

        return {
            'best_month': month_names[best_month_idx - 1],
            'worst_month': month_names[worst_month_idx - 1],
            'monthly_averages': {
                month_names[i]: float(monthly_avg.loc[i + 1, 'mean'])
                for i in range(12) if (i + 1) in monthly_avg.index
            }
        }

    def _detect_frequencies(self, ts: pd.Series, top_n: int = 5) -> List[Dict]:
        """Detect dominant frequencies using FFT"""
        # Remove trend
        detrended = ts - ts.rolling(window=7, center=True).mean()
        detrended = detrended.dropna()

        # Apply FFT
        fft_values = fft(detrended.values)
        frequencies = np.fft.fftfreq(len(detrended))

        # Get positive frequencies only
        positive_freq_idx = frequencies > 0
        frequencies = frequencies[positive_freq_idx]
        magnitudes = np.abs(fft_values[positive_freq_idx])

        # Find top frequencies
        top_indices = np.argsort(magnitudes)[-top_n:][::-1]

        cycles = []
        for idx in top_indices:
            freq = frequencies[idx]
            period_days = 1 / freq if freq > 0 else 0
            cycles.append({
                'period_days': float(period_days),
                'magnitude': float(magnitudes[idx])
            })

        return cycles

    async def analyze_weather_correlation(
        self,
        mood_data: List[Dict],
        weather_data: List[Dict]
    ) -> Dict:
        """
        Analyze correlation between mood and weather

        Args:
            mood_data: Historical mood data
            weather_data: Weather data (temperature, precipitation, etc.)

        Returns:
            Correlation analysis results
        """
        try:
            # Merge datasets
            mood_df = pd.DataFrame(mood_data)
            weather_df = pd.DataFrame(weather_data)

            mood_df['date'] = pd.to_datetime(mood_df['date'])
            weather_df['date'] = pd.to_datetime(weather_df['date'])

            merged = pd.merge(mood_df, weather_df, on='date', how='inner')

            if len(merged) < 30:
                return {
                    'sufficient_data': False,
                    'note': 'Need at least 30 days of combined data'
                }

            # Calculate correlations
            correlations = {}
            weather_features = ['temperature', 'precipitation', 'humidity', 'pressure', 'cloud_cover']

            for feature in weather_features:
                if feature in merged.columns:
                    corr, p_value = stats.pearsonr(merged['mood_score'], merged[feature])
                    correlations[feature] = {
                        'correlation': float(corr),
                        'p_value': float(p_value),
                        'significant': p_value < 0.05
                    }

            # Find strongest correlations
            significant_correlations = {
                k: v for k, v in correlations.items()
                if v.get('significant', False)
            }

            return {
                'sufficient_data': True,
                'n_days': len(merged),
                'correlations': correlations,
                'significant_correlations': significant_correlations,
                'summary': self._generate_correlation_summary(correlations)
            }

        except Exception as e:
            logger.error(f"Weather correlation analysis error: {e}")
            return {'sufficient_data': False, 'error': str(e)}

    def _generate_correlation_summary(self, correlations: Dict) -> str:
        """Generate human-readable summary of correlations"""
        if not correlations:
            return "No weather correlations found"

        significant = [
            (k, v['correlation'])
            for k, v in correlations.items()
            if v.get('significant', False)
        ]

        if not significant:
            return "No significant weather correlations detected"

        strongest = max(significant, key=lambda x: abs(x[1]))
        direction = "positively" if strongest[1] > 0 else "negatively"

        return f"Mood is most {direction} correlated with {strongest[0]} (r={strongest[1]:.2f})"

    async def analyze_sleep_patterns(
        self,
        mood_data: List[Dict],
        sleep_data: List[Dict]
    ) -> Dict:
        """
        Analyze relationship between sleep and mood

        Args:
            mood_data: Historical mood data
            sleep_data: Sleep data (hours, quality, etc.)

        Returns:
            Sleep-mood correlation analysis
        """
        try:
            # Merge datasets
            mood_df = pd.DataFrame(mood_data)
            sleep_df = pd.DataFrame(sleep_data)

            mood_df['date'] = pd.to_datetime(mood_df['date'])
            sleep_df['date'] = pd.to_datetime(sleep_df['date'])

            merged = pd.merge(mood_df, sleep_df, on='date', how='inner')

            if len(merged) < 14:
                return {
                    'sufficient_data': False,
                    'note': 'Need at least 14 days of combined data'
                }

            # Analyze sleep duration
            sleep_duration_corr, sleep_p = stats.pearsonr(
                merged['mood_score'],
                merged['sleep_hours']
            )

            # Analyze sleep quality if available
            sleep_quality_corr = None
            if 'sleep_quality' in merged.columns:
                sleep_quality_corr, quality_p = stats.pearsonr(
                    merged['mood_score'],
                    merged['sleep_quality']
                )

            # Find optimal sleep range
            optimal_range = self._find_optimal_sleep_range(merged)

            # Analyze sleep consistency
            sleep_consistency = merged['sleep_hours'].std()

            return {
                'sufficient_data': True,
                'n_days': len(merged),
                'sleep_duration_correlation': {
                    'correlation': float(sleep_duration_corr),
                    'p_value': float(sleep_p),
                    'significant': sleep_p < 0.05
                },
                'sleep_quality_correlation': {
                    'correlation': float(sleep_quality_corr),
                    'p_value': float(quality_p),
                    'significant': quality_p < 0.05
                } if sleep_quality_corr else None,
                'optimal_sleep_range': optimal_range,
                'sleep_consistency_std': float(sleep_consistency),
                'recommendation': self._generate_sleep_recommendation(
                    sleep_duration_corr,
                    optimal_range,
                    sleep_consistency
                )
            }

        except Exception as e:
            logger.error(f"Sleep pattern analysis error: {e}")
            return {'sufficient_data': False, 'error': str(e)}

    def _find_optimal_sleep_range(self, df: pd.DataFrame) -> Dict:
        """Find sleep range associated with best mood"""
        # Group by sleep hours (rounded to nearest 0.5)
        df['sleep_rounded'] = (df['sleep_hours'] * 2).round() / 2
        grouped = df.groupby('sleep_rounded')['mood_score'].agg(['mean', 'std', 'count'])

        # Find range with best mood
        best_sleep = grouped['mean'].idxmax()

        return {
            'optimal_hours': float(best_sleep),
            'average_mood': float(grouped.loc[best_sleep, 'mean']),
            'range': f"{best_sleep - 0.5} to {best_sleep + 0.5} hours"
        }

    def _generate_sleep_recommendation(
        self,
        correlation: float,
        optimal_range: Dict,
        consistency_std: float
    ) -> str:
        """Generate sleep recommendation based on analysis"""
        recommendations = []

        if correlation > 0.3:
            recommendations.append(
                f"Aim for {optimal_range['optimal_hours']:.1f} hours of sleep for optimal mood"
            )

        if consistency_std > 2:
            recommendations.append("Try to maintain a more consistent sleep schedule")

        return "; ".join(recommendations) if recommendations else "Continue monitoring sleep patterns"


# Singleton instance
_prediction_service_instance = None


def get_prediction_service() -> PredictionService:
    """Get or create prediction service singleton"""
    global _prediction_service_instance
    if _prediction_service_instance is None:
        _prediction_service_instance = PredictionService()
    return _prediction_service_instance
