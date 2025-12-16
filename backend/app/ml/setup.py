"""
Setup and initialization script for ML services
Downloads models, initializes services, and verifies installation
"""

import logging
import sys
from pathlib import Path
import nltk
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_nltk_data():
    """Download required NLTK data"""
    logger.info("Downloading NLTK data...")
    packages = ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'wordnet']

    for package in packages:
        try:
            nltk.download(package, quiet=True)
            logger.info(f"✓ Downloaded {package}")
        except Exception as e:
            logger.error(f"✗ Failed to download {package}: {e}")
            return False

    return True


def download_transformer_models():
    """Pre-download transformer models"""
    logger.info("Downloading transformer models...")

    models = [
        "nlptown/bert-base-multilingual-uncased-sentiment",
        "j-hartmann/emotion-english-distilroberta-base",
        "facebook/bart-large-mnli"
    ]

    for model_name in models:
        try:
            logger.info(f"Downloading {model_name}...")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            logger.info(f"✓ Downloaded {model_name}")
        except Exception as e:
            logger.error(f"✗ Failed to download {model_name}: {e}")
            return False

    return True


def check_dependencies():
    """Check if all dependencies are installed"""
    logger.info("Checking dependencies...")

    required_packages = [
        'transformers',
        'torch',
        'sklearn',
        'tensorflow',
        'nltk',
        'textblob',
        'scipy',
        'pandas',
        'numpy'
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package} installed")
        except ImportError:
            logger.error(f"✗ {package} not installed")
            missing.append(package)

    if missing:
        logger.error(f"Missing packages: {', '.join(missing)}")
        logger.error("Install with: pip install " + " ".join(missing))
        return False

    return True


def check_gpu():
    """Check GPU availability"""
    logger.info("Checking GPU availability...")

    if torch.cuda.is_available():
        logger.info(f"✓ GPU available: {torch.cuda.get_device_name(0)}")
        logger.info(f"  CUDA version: {torch.version.cuda}")
        logger.info(f"  GPU count: {torch.cuda.device_count()}")
        return True
    else:
        logger.warning("✗ No GPU available, will use CPU")
        logger.warning("  For better performance, consider installing CUDA")
        return False


def create_model_directories():
    """Create directories for model storage"""
    logger.info("Creating model directories...")

    dirs = [
        "./ml_models",
        "./ml_models/lstm",
        "./ml_models/transformer",
        "./ml_models/cache"
    ]

    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Created {directory}")

    return True


def verify_installation():
    """Verify ML module installation"""
    logger.info("Verifying ML module installation...")

    try:
        from app.ml.nlp_service import get_nlp_service
        from app.ml.prediction_service import get_prediction_service
        from app.ml.collaborative_filtering import get_collaborative_filtering_service

        logger.info("✓ ML modules importable")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to import ML modules: {e}")
        return False


def run_setup(skip_model_download: bool = False):
    """Run complete setup process"""
    logger.info("=" * 60)
    logger.info("ML Module Setup")
    logger.info("=" * 60)

    steps = [
        ("Checking dependencies", check_dependencies),
        ("Checking GPU", check_gpu),
        ("Creating directories", create_model_directories),
        ("Downloading NLTK data", download_nltk_data),
        ("Verifying installation", verify_installation)
    ]

    if not skip_model_download:
        steps.insert(4, ("Downloading transformer models", download_transformer_models))

    failed_steps = []

    for step_name, step_func in steps:
        logger.info(f"\n[{step_name}]")
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            logger.error(f"Error in {step_name}: {e}")
            failed_steps.append(step_name)

    logger.info("\n" + "=" * 60)
    if failed_steps:
        logger.error("Setup completed with errors:")
        for step in failed_steps:
            logger.error(f"  ✗ {step}")
        logger.info("\nSome features may not work correctly.")
        return False
    else:
        logger.info("✓ Setup completed successfully!")
        logger.info("\nML module is ready to use.")
        return True


def quick_test():
    """Run quick functionality test"""
    logger.info("\n" + "=" * 60)
    logger.info("Running Quick Test")
    logger.info("=" * 60)

    try:
        from app.ml.nlp_service import get_nlp_service
        import asyncio

        logger.info("\nTesting NLP service...")
        nlp_service = get_nlp_service()

        test_text = "I feel really happy and optimistic today!"
        result = asyncio.run(nlp_service.analyze_journal_entry(test_text))

        logger.info(f"✓ Sentiment: {result['sentiment']['label']} ({result['sentiment']['score']:.2f})")
        logger.info(f"✓ Primary emotion: {result['emotions']['primary_emotion']} ({result['emotions']['primary_score']:.2f})")
        logger.info(f"✓ Crisis detected: {result['crisis_detection']['crisis_detected']}")

        logger.info("\n✓ Quick test passed!")
        return True

    except Exception as e:
        logger.error(f"\n✗ Quick test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Setup ML module for Firefly")
    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="Skip downloading transformer models (for faster setup)"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run quick functionality test after setup"
    )

    args = parser.parse_args()

    success = run_setup(skip_model_download=args.skip_models)

    if success and args.test:
        quick_test()

    sys.exit(0 if success else 1)
