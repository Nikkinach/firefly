"""
Crisis Detection Service - Safety-critical component
"""
from typing import Dict, List, Tuple
import re


class CrisisDetectionService:
    """Multi-layer crisis detection system"""

    # Crisis keywords with risk weights
    CRISIS_KEYWORDS = {
        # High risk - immediate concern
        "suicide": 1.0,
        "kill myself": 1.0,
        "end it all": 1.0,
        "want to die": 1.0,
        "better off dead": 1.0,
        "no reason to live": 0.9,
        "can't go on": 0.8,
        "ending my life": 1.0,
        "take my life": 1.0,

        # Moderate risk - concerning
        "self harm": 0.7,
        "hurt myself": 0.7,
        "cutting": 0.6,
        "hopeless": 0.5,
        "worthless": 0.5,
        "burden": 0.5,
        "nobody cares": 0.6,
        "give up": 0.5,
        "can't take": 0.6,

        # Temporal markers - increase risk when combined
        "tonight": 0.3,
        "soon": 0.3,
        "goodbye": 0.4,
        "final": 0.3,
        "last": 0.2,
    }

    # Simple emotion classification keywords
    EMOTION_KEYWORDS = {
        "anxiety": ["anxious", "worried", "nervous", "panic", "scared", "fear"],
        "sadness": ["sad", "depressed", "down", "low", "crying", "tears"],
        "anger": ["angry", "frustrated", "mad", "furious", "rage", "irritated"],
        "overwhelm": ["overwhelmed", "too much", "can't handle", "drowning"],
        "stress": ["stressed", "pressure", "tense", "strain"],
        "calm": ["calm", "peaceful", "relaxed", "serene"],
        "joy": ["happy", "joyful", "excited", "grateful", "content"],
    }

    @staticmethod
    def analyze_text(text: str) -> Dict:
        """
        Analyze text for crisis indicators and emotions.
        Returns risk assessment and detected emotions.
        """
        if not text:
            return {
                "risk_score": 0.0,
                "risk_level": "low",
                "crisis_flagged": False,
                "keywords_found": [],
                "ai_emotion_primary": None,
                "recommended_response": "continue_normal"
            }

        text_lower = text.lower()

        # Stage 1: Fast keyword scan
        keyword_score, keywords_found = CrisisDetectionService._keyword_scan(text_lower)

        # Stage 2: Emotion detection
        primary_emotion = CrisisDetectionService._detect_emotion(text_lower)

        # Determine risk level
        crisis_flagged = False
        risk_level = "low"
        recommended_response = "continue_normal"

        if keyword_score > 0.7:
            risk_level = "critical"
            crisis_flagged = True
            recommended_response = "show_crisis_resources"
        elif keyword_score > 0.5:
            risk_level = "high"
            crisis_flagged = True
            recommended_response = "show_crisis_resources"
        elif keyword_score > 0.3:
            risk_level = "moderate"
            recommended_response = "offer_safety_check"
        else:
            risk_level = "low"
            recommended_response = "continue_normal"

        return {
            "risk_score": min(keyword_score, 1.0),
            "risk_level": risk_level,
            "crisis_flagged": crisis_flagged,
            "keywords_found": keywords_found,
            "ai_emotion_primary": primary_emotion,
            "recommended_response": recommended_response
        }

    @staticmethod
    def _keyword_scan(text: str) -> Tuple[float, List[str]]:
        """Scan text for crisis keywords"""
        found_keywords = []
        total_score = 0.0

        for keyword, weight in CrisisDetectionService.CRISIS_KEYWORDS.items():
            if keyword in text:
                found_keywords.append(keyword)
                total_score += weight

        # Normalize score (cap at 1.0)
        return min(total_score, 1.0), found_keywords

    @staticmethod
    def _detect_emotion(text: str) -> str:
        """Simple keyword-based emotion detection"""
        emotion_scores = {}

        for emotion, keywords in CrisisDetectionService.EMOTION_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                emotion_scores[emotion] = score

        if not emotion_scores:
            return "neutral"

        return max(emotion_scores, key=emotion_scores.get)

    @staticmethod
    def get_crisis_resources() -> Dict:
        """Return crisis resource information"""
        return {
            "hotlines": [
                {
                    "name": "988 Suicide & Crisis Lifeline",
                    "number": "988",
                    "description": "24/7 crisis support",
                    "type": "call"
                },
                {
                    "name": "Crisis Text Line",
                    "number": "741741",
                    "description": "Text HOME to connect",
                    "type": "text"
                },
                {
                    "name": "National Suicide Prevention Lifeline",
                    "number": "1-800-273-8255",
                    "description": "24/7 support",
                    "type": "call"
                }
            ],
            "message": "You matter. If you're having thoughts of suicide, please reach out to one of these resources immediately.",
            "safe_now_options": [
                "Try a calming exercise",
                "Review your safety plan",
                "Contact someone you trust",
                "Return to app"
            ]
        }
