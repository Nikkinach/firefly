"""
Natural Language Processing Service for Journal Analysis
Provides sentiment analysis, emotion classification, crisis detection, and theme extraction
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np
from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSequenceClassification,
    AutoModelForTokenClassification
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import torch

logger = logging.getLogger(__name__)


class NLPService:
    """Advanced NLP service for mental health journal analysis"""

    def __init__(self):
        """Initialize NLP models and resources"""
        self._setup_nltk()
        self._initialize_models()
        self._setup_crisis_keywords()

    def _setup_nltk(self):
        """Download required NLTK data"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('wordnet', quiet=True)
        except Exception as e:
            logger.warning(f"NLTK download warning: {e}")

    def _initialize_models(self):
        """Initialize transformer models for various NLP tasks"""
        try:
            # Sentiment Analysis - fine-tuned model
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                device=0 if torch.cuda.is_available() else -1
            )

            # Emotion Classification - 6 basic emotions
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                device=0 if torch.cuda.is_available() else -1,
                top_k=None
            )

            # Zero-shot classification for crisis detection
            self.crisis_classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=0 if torch.cuda.is_available() else -1
            )

            logger.info("NLP models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NLP models: {e}")
            raise

    def _setup_crisis_keywords(self):
        """Define crisis keywords and patterns with severity weights"""
        self.crisis_keywords = {
            'critical': {
                'keywords': [
                    'suicide', 'kill myself', 'end my life', 'want to die',
                    'no reason to live', 'better off dead', 'ending it all',
                    'self-harm', 'cutting myself', 'overdose'
                ],
                'weight': 1.0
            },
            'high': {
                'keywords': [
                    'hopeless', 'can\'t go on', 'unbearable', 'worthless',
                    'hate myself', 'no point', 'give up', 'can\'t take it'
                ],
                'weight': 0.75
            },
            'moderate': {
                'keywords': [
                    'depressed', 'anxious', 'panic', 'scared', 'overwhelmed',
                    'desperate', 'alone', 'isolated', 'crying'
                ],
                'weight': 0.5
            },
            'low': {
                'keywords': [
                    'sad', 'worried', 'stressed', 'tired', 'frustrated',
                    'upset', 'down', 'lonely'
                ],
                'weight': 0.25
            }
        }

        # Compile regex patterns for efficiency
        self.crisis_patterns = {}
        for severity, data in self.crisis_keywords.items():
            patterns = [re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
                       for kw in data['keywords']]
            self.crisis_patterns[severity] = {
                'patterns': patterns,
                'weight': data['weight']
            }

    async def analyze_journal_entry(self, text: str) -> Dict:
        """
        Comprehensive analysis of a journal entry

        Args:
            text: Journal entry text

        Returns:
            Dictionary containing all NLP analysis results
        """
        if not text or len(text.strip()) < 10:
            return self._empty_analysis()

        try:
            # Run all analyses
            sentiment = await self.analyze_sentiment(text)
            emotions = await self.classify_emotions(text)
            crisis = await self.detect_crisis_keywords(text)
            themes = await self.extract_themes([text])

            return {
                'sentiment': sentiment,
                'emotions': emotions,
                'crisis_detection': crisis,
                'themes': themes,
                'analyzed_at': datetime.utcnow().isoformat(),
                'text_length': len(text),
                'word_count': len(text.split())
            }
        except Exception as e:
            logger.error(f"Error analyzing journal entry: {e}")
            return self._empty_analysis()

    async def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment using fine-tuned transformer model

        Args:
            text: Input text

        Returns:
            Sentiment analysis results with score and label
        """
        try:
            # Truncate text if too long (model limit is typically 512 tokens)
            max_length = 500
            if len(text) > max_length:
                # Analyze first and last portions
                first_part = text[:max_length//2]
                last_part = text[-max_length//2:]
                text_to_analyze = first_part + " " + last_part
            else:
                text_to_analyze = text

            result = self.sentiment_analyzer(text_to_analyze)[0]

            # Convert 5-star rating to normalized score
            # Model outputs: 1 star (very negative) to 5 stars (very positive)
            star_rating = int(result['label'].split()[0])
            normalized_score = (star_rating - 1) / 4  # 0.0 to 1.0

            # Map to sentiment labels
            if normalized_score < 0.3:
                sentiment_label = 'negative'
            elif normalized_score < 0.7:
                sentiment_label = 'neutral'
            else:
                sentiment_label = 'positive'

            return {
                'score': normalized_score,
                'label': sentiment_label,
                'confidence': result['score'],
                'raw_rating': star_rating
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {'score': 0.5, 'label': 'neutral', 'confidence': 0.0, 'error': str(e)}

    async def classify_emotions(self, text: str) -> Dict:
        """
        Classify emotions using transformer model
        Detects: anger, disgust, fear, joy, neutral, sadness, surprise

        Args:
            text: Input text

        Returns:
            Emotion classification results
        """
        try:
            # Truncate if needed
            max_length = 500
            text_to_analyze = text[:max_length] if len(text) > max_length else text

            results = self.emotion_classifier(text_to_analyze)[0]

            # Convert to dictionary with scores
            emotions = {item['label']: item['score'] for item in results}

            # Get primary emotion
            primary_emotion = max(emotions.items(), key=lambda x: x[1])

            return {
                'primary_emotion': primary_emotion[0],
                'primary_score': primary_emotion[1],
                'all_emotions': emotions
            }
        except Exception as e:
            logger.error(f"Emotion classification error: {e}")
            return {
                'primary_emotion': 'neutral',
                'primary_score': 0.0,
                'all_emotions': {},
                'error': str(e)
            }

    async def detect_crisis_keywords(self, text: str) -> Dict:
        """
        Advanced crisis keyword detection with severity scoring

        Args:
            text: Journal entry text

        Returns:
            Crisis detection results with severity and matched keywords
        """
        text_lower = text.lower()
        detected_keywords = []
        total_weight = 0.0
        severity_counts = {'critical': 0, 'high': 0, 'moderate': 0, 'low': 0}

        # Check for keyword matches
        for severity, data in self.crisis_patterns.items():
            for pattern in data['patterns']:
                matches = pattern.findall(text)
                if matches:
                    for match in matches:
                        detected_keywords.append({
                            'keyword': match,
                            'severity': severity,
                            'weight': data['weight']
                        })
                        total_weight += data['weight']
                        severity_counts[severity] += 1

        # Calculate crisis score (0.0 to 1.0)
        crisis_score = min(total_weight / 3.0, 1.0)  # Normalize to max of 1.0

        # Use zero-shot classification for additional context
        try:
            crisis_labels = [
                "suicidal ideation",
                "self-harm",
                "severe depression",
                "mental health crisis",
                "normal mood"
            ]

            classification = self.crisis_classifier(
                text[:500],  # Truncate for model
                candidate_labels=crisis_labels
            )

            crisis_classification = {
                label: score
                for label, score in zip(classification['labels'], classification['scores'])
            }
        except Exception as e:
            logger.warning(f"Zero-shot classification failed: {e}")
            crisis_classification = {}

        # Determine overall risk level
        if crisis_score >= 0.75 or severity_counts['critical'] > 0:
            risk_level = 'critical'
        elif crisis_score >= 0.5 or severity_counts['high'] > 0:
            risk_level = 'high'
        elif crisis_score >= 0.25 or severity_counts['moderate'] > 0:
            risk_level = 'moderate'
        elif crisis_score > 0:
            risk_level = 'low'
        else:
            risk_level = 'none'

        return {
            'crisis_detected': crisis_score > 0,
            'crisis_score': crisis_score,
            'risk_level': risk_level,
            'matched_keywords': detected_keywords,
            'severity_counts': severity_counts,
            'ml_classification': crisis_classification,
            'requires_immediate_attention': risk_level in ['critical', 'high']
        }

    async def extract_themes(self, texts: List[str], n_topics: int = 5) -> Dict:
        """
        Extract themes from journal entries using LDA topic modeling

        Args:
            texts: List of journal entry texts
            n_topics: Number of topics to extract

        Returns:
            Extracted themes and keywords
        """
        if not texts or len(texts) < 3:
            return {'themes': [], 'note': 'Insufficient data for theme extraction'}

        try:
            # Preprocess texts
            processed_texts = [self._preprocess_text(text) for text in texts]
            processed_texts = [t for t in processed_texts if t]  # Remove empty

            if len(processed_texts) < 3:
                return {'themes': [], 'note': 'Insufficient valid text for analysis'}

            # Create TF-IDF matrix
            vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                min_df=2,
                max_df=0.8
            )

            tfidf_matrix = vectorizer.fit_transform(processed_texts)

            # Apply LDA
            n_topics = min(n_topics, len(processed_texts))
            lda_model = LatentDirichletAllocation(
                n_components=n_topics,
                random_state=42,
                max_iter=20
            )

            lda_model.fit(tfidf_matrix)

            # Extract themes
            feature_names = vectorizer.get_feature_names_out()
            themes = []

            for topic_idx, topic in enumerate(lda_model.components_):
                top_indices = topic.argsort()[-10:][::-1]
                top_words = [feature_names[i] for i in top_indices]
                top_weights = [float(topic[i]) for i in top_indices]

                themes.append({
                    'theme_id': topic_idx,
                    'keywords': top_words[:5],
                    'all_keywords': top_words,
                    'weights': top_weights,
                    'theme_name': self._generate_theme_name(top_words[:3])
                })

            return {
                'themes': themes,
                'n_documents': len(texts),
                'n_topics': n_topics
            }

        except Exception as e:
            logger.error(f"Theme extraction error: {e}")
            return {'themes': [], 'error': str(e)}

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for theme extraction"""
        try:
            # Remove special characters and digits
            text = re.sub(r'[^a-zA-Z\s]', '', text)

            # Tokenize and remove stopwords
            tokens = word_tokenize(text.lower())
            stop_words = set(stopwords.words('english'))
            tokens = [t for t in tokens if t not in stop_words and len(t) > 3]

            return ' '.join(tokens)
        except Exception as e:
            logger.warning(f"Text preprocessing error: {e}")
            return text

    def _generate_theme_name(self, keywords: List[str]) -> str:
        """Generate a human-readable theme name from keywords"""
        return ' & '.join(keywords[:3]).title()

    def _empty_analysis(self) -> Dict:
        """Return empty analysis structure"""
        return {
            'sentiment': {'score': 0.5, 'label': 'neutral', 'confidence': 0.0},
            'emotions': {'primary_emotion': 'neutral', 'primary_score': 0.0, 'all_emotions': {}},
            'crisis_detection': {
                'crisis_detected': False,
                'crisis_score': 0.0,
                'risk_level': 'none',
                'matched_keywords': [],
                'requires_immediate_attention': False
            },
            'themes': {'themes': []},
            'analyzed_at': datetime.utcnow().isoformat(),
            'text_length': 0,
            'word_count': 0
        }


# Singleton instance
_nlp_service_instance = None


def get_nlp_service() -> NLPService:
    """Get or create NLP service singleton"""
    global _nlp_service_instance
    if _nlp_service_instance is None:
        _nlp_service_instance = NLPService()
    return _nlp_service_instance
