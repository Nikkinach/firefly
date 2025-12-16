"""
Configuration for ML Services
Centralized configuration for models, parameters, and resources
"""

from pydantic import BaseModel
from typing import Optional, List
import os


class NLPConfig(BaseModel):
    """Configuration for NLP service"""
    sentiment_model: str = "nlptown/bert-base-multilingual-uncased-sentiment"
    emotion_model: str = "j-hartmann/emotion-english-distilroberta-base"
    crisis_model: str = "facebook/bart-large-mnli"

    # Device configuration
    use_gpu: bool = True
    device: int = 0  # GPU device index

    # Text processing
    max_text_length: int = 500
    min_text_length: int = 10

    # Theme extraction
    min_entries_for_themes: int = 3
    max_topics: int = 5
    max_features_tfidf: int = 1000


class PredictionConfig(BaseModel):
    """Configuration for prediction service"""
    # LSTM parameters
    lstm_sequence_length: int = 14
    lstm_n_features: int = 5
    lstm_hidden_units: List[int] = [128, 64, 32]
    lstm_dropout_rate: float = 0.2
    lstm_prediction_horizon: int = 7

    # Training parameters
    default_epochs: int = 50
    batch_size: int = 16
    learning_rate: float = 0.001
    early_stopping_patience: int = 10
    validation_split: float = 0.2

    # Data requirements
    min_training_days: int = 21
    min_prediction_days: int = 14
    min_pattern_days: int = 90

    # Confidence intervals
    monte_carlo_iterations: int = 100
    confidence_level: float = 0.95


class CollaborativeFilteringConfig(BaseModel):
    """Configuration for collaborative filtering"""
    # Clustering
    default_n_clusters: int = 5
    min_users_for_clustering: int = 10
    clustering_method: str = "kmeans"  # kmeans or dbscan

    # DBSCAN parameters
    dbscan_eps: float = 0.5
    dbscan_min_samples: int = 3

    # Recommendations
    default_similar_users: int = 10
    default_recommendations: int = 5
    min_confidence_threshold: float = 0.3

    # A/B Testing
    default_test_duration_days: int = 30
    min_test_duration_days: int = 7
    max_test_duration_days: int = 90
    significance_level: float = 0.05

    # Privacy
    anonymization_algorithm: str = "sha256"
    profile_id_length: int = 16


class MLConfig(BaseModel):
    """Master ML configuration"""
    nlp: NLPConfig = NLPConfig()
    prediction: PredictionConfig = PredictionConfig()
    collaborative_filtering: CollaborativeFilteringConfig = CollaborativeFilteringConfig()

    # Model storage
    model_storage_path: str = "./ml_models"
    cache_models: bool = True

    # Logging
    log_level: str = "INFO"
    log_predictions: bool = True
    log_analyses: bool = True

    # Performance
    enable_batch_processing: bool = True
    max_batch_size: int = 32
    async_processing: bool = True

    # Feature flags
    enable_crisis_detection: bool = True
    enable_predictions: bool = True
    enable_collaborative_filtering: bool = True
    enable_ab_testing: bool = True


# Global configuration instance
_config: Optional[MLConfig] = None


def get_ml_config() -> MLConfig:
    """Get ML configuration singleton"""
    global _config
    if _config is None:
        _config = MLConfig()
    return _config


def update_ml_config(**kwargs) -> MLConfig:
    """Update ML configuration"""
    global _config
    if _config is None:
        _config = MLConfig(**kwargs)
    else:
        for key, value in kwargs.items():
            if hasattr(_config, key):
                setattr(_config, key, value)
    return _config


# Environment-based configuration
def load_config_from_env() -> MLConfig:
    """Load configuration from environment variables"""
    config_dict = {}

    # NLP config
    if os.getenv("ML_USE_GPU"):
        config_dict.setdefault("nlp", {})["use_gpu"] = os.getenv("ML_USE_GPU").lower() == "true"

    # Prediction config
    if os.getenv("ML_LSTM_EPOCHS"):
        config_dict.setdefault("prediction", {})["default_epochs"] = int(os.getenv("ML_LSTM_EPOCHS"))

    # Model storage
    if os.getenv("ML_MODEL_PATH"):
        config_dict["model_storage_path"] = os.getenv("ML_MODEL_PATH")

    return MLConfig(**config_dict)
