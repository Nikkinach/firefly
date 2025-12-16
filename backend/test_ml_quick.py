"""
Quick ML Test - Tests NLP features without heavy dependencies
Run this first to verify basic functionality
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("QUICK ML TEST - NLP FEATURES")
print("=" * 80)

async def test_imports():
    """Test if ML modules can be imported"""
    print("\n[TEST 1] Testing imports...")
    try:
        from app.ml import nlp_service, prediction_service, collaborative_filtering
        print("✓ ML modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_nlp_service_init():
    """Test NLP service initialization"""
    print("\n[TEST 2] Initializing NLP service...")
    try:
        print("  This will download transformer models (~1.5GB) on first run...")
        print("  This may take 5-10 minutes depending on your internet connection.")
        print("  Please wait...")

        from app.ml.nlp_service import get_nlp_service
        nlp = get_nlp_service()
        print("✓ NLP service initialized")
        return nlp
    except Exception as e:
        print(f"✗ NLP initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_sentiment_analysis(nlp):
    """Test sentiment analysis"""
    print("\n[TEST 3] Testing sentiment analysis...")

    test_texts = {
        'positive': "I feel amazing today! Everything is going great and I'm so happy!",
        'negative': "I feel terrible today. Everything is going wrong and I'm really sad.",
        'neutral': "Today was an ordinary day. Nothing special happened."
    }

    try:
        for category, text in test_texts.items():
            result = await nlp.analyze_sentiment(text)
            print(f"\n  {category.upper()} text:")
            print(f"    \"{text[:50]}...\"")
            print(f"    Result: {result['label']} (score: {result['score']:.2f})")

        print("\n✓ Sentiment analysis working!")
        return True
    except Exception as e:
        print(f"\n✗ Sentiment analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_emotion_classification(nlp):
    """Test emotion classification"""
    print("\n[TEST 4] Testing emotion classification...")

    text = "I'm feeling anxious about tomorrow's presentation but also excited about the opportunity."

    try:
        result = await nlp.classify_emotions(text)
        print(f"\n  Text: \"{text}\"")
        print(f"  Primary emotion: {result['primary_emotion']} ({result['primary_score']:.2f})")
        print(f"  All emotions detected: {len(result['all_emotions'])}")

        print("\n✓ Emotion classification working!")
        return True
    except Exception as e:
        print(f"\n✗ Emotion classification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_crisis_detection(nlp):
    """Test crisis detection"""
    print("\n[TEST 5] Testing crisis detection...")

    test_cases = [
        ("Safe text", "I had a good day today. Looking forward to tomorrow."),
        ("Concerning text", "I feel so hopeless and worthless. Everything is unbearable.")
    ]

    try:
        for label, text in test_cases:
            result = await nlp.detect_crisis_keywords(text)
            print(f"\n  {label}:")
            print(f"    Crisis detected: {result['crisis_detected']}")
            print(f"    Risk level: {result['risk_level']}")
            if result['crisis_detected']:
                print(f"    Matched {len(result['matched_keywords'])} keywords")
                print(f"    Requires attention: {result['requires_immediate_attention']}")

        print("\n✓ Crisis detection working!")
        return True
    except Exception as e:
        print(f"\n✗ Crisis detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_full_analysis(nlp):
    """Test complete journal analysis"""
    print("\n[TEST 6] Testing full journal analysis...")

    text = """Today was challenging but I managed to cope. Started feeling anxious in the morning
    after a bad night's sleep. Decided to go for a walk which helped calm my mind.
    Had a good conversation with a friend who really understood what I'm going through.
    Feeling more hopeful now, though still a bit worried about tomorrow."""

    try:
        result = await nlp.analyze_journal_entry(text)

        print(f"\n  Analyzing: \"{text[:60]}...\"")
        print(f"\n  Results:")
        print(f"    Sentiment: {result['sentiment']['label']} ({result['sentiment']['score']:.2f})")
        print(f"    Primary emotion: {result['emotions']['primary_emotion']}")
        print(f"    Crisis risk: {result['crisis_detection']['risk_level']}")
        print(f"    Word count: {result['word_count']}")

        print("\n✓ Full analysis working!")
        return True
    except Exception as e:
        print(f"\n✗ Full analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all quick tests"""
    print("\nStarting ML tests...")
    print("Note: First run will download models (~1.5GB)\n")

    # Test imports
    if not await test_imports():
        print("\n❌ FAILED: Could not import ML modules")
        return

    # Initialize NLP service
    nlp = await test_nlp_service_init()
    if nlp is None:
        print("\n❌ FAILED: Could not initialize NLP service")
        print("\nPossible issues:")
        print("  1. Missing dependencies (transformers, torch, nltk, textblob)")
        print("  2. No internet connection for model download")
        print("  3. Insufficient disk space")
        return

    # Run NLP tests
    tests_passed = 0
    tests_total = 4

    if await test_sentiment_analysis(nlp):
        tests_passed += 1

    if await test_emotion_classification(nlp):
        tests_passed += 1

    if await test_crisis_detection(nlp):
        tests_passed += 1

    if await test_full_analysis(nlp):
        tests_passed += 1

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"\nTests passed: {tests_passed}/{tests_total}")

    if tests_passed == tests_total:
        print("\n🎉 ALL NLP TESTS PASSED!")
        print("\nNLP features are working correctly:")
        print("  ✓ Sentiment Analysis")
        print("  ✓ Emotion Classification")
        print("  ✓ Crisis Detection")
        print("  ✓ Full Journal Analysis")
        print("\nNext steps:")
        print("  1. Install remaining dependencies: pip install numpy pandas scikit-learn tensorflow")
        print("  2. Run full test suite: python test_ml_complete.py")
    else:
        print(f"\n❌ {tests_total - tests_passed} test(s) failed")
        print("Please check the errors above")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
