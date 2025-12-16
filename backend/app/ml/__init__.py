"""
Machine Learning and NLP Module for Firefly
Provides advanced analytics, predictions, and recommendations
"""

from .nlp_service import NLPService
from .prediction_service import PredictionService
from .collaborative_filtering import CollaborativeFilteringService

__all__ = [
    'NLPService',
    'PredictionService',
    'CollaborativeFilteringService'
]
