# ML Testing Guide

## Current Status

### ✅ Completed
1. **ML Module Implementation** - All 3 major components built
2. **Database Models** - ML-specific models created (fixed UUID compatibility)
3. **API Endpoints** - 20+ endpoints ready
4. **Documentation** - Complete docs and guides
5. **Test Scripts** - Comprehensive testing suite created

### 🔄 In Progress
- Installing ML dependencies (transformers, torch, nltk, textblob)
- Dependencies being installed:
  - ✅ numpy, pandas, scikit-learn, scipy (INSTALLED)
  - 🔄 transformers, torch, nltk, textblob (INSTALLING...)

## Testing Options

### Option 1: Quick NLP Test (Recommended First)
Tests basic NLP functionality without all dependencies.

```bash
cd backend
python test_ml_quick.py
```

**Features tested:**
- ✓ Sentiment Analysis
- ✓ Emotion Classification
- ✓ Crisis Detection
- ✓ Full Journal Analysis

**Note:** First run downloads transformer models (~1.5GB, takes 5-10 minutes)

### Option 2: Comprehensive Test Suite
Tests all ML features including predictions and collaborative filtering.

```bash
cd backend
python test_ml_complete.py
```

**Features tested:**
- ✓ All NLP features (4 tests)
- ✓ LSTM Model Building & Training (3 tests)
- ✓ Mood Prediction & Patterns (3 tests)
- ✓ Collaborative Filtering (4 tests)
- ✓ A/B Testing (1 test)

**Total:** 15 comprehensive tests

### Option 3: Integration with Database
Test with actual database and API.

```bash
# 1. Start backend
cd backend
python -m uvicorn app.main:app --reload

# 2. Test API endpoints (in another terminal)
# Sentiment analysis
curl -X POST "http://localhost:8000/api/v1/ml/analyze-journal" \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel happy today!"}'

# Health check
curl "http://localhost:8000/api/v1/ml/health"
```

## Required Dependencies

### Data Science (✅ INSTALLED)
```
numpy==2.3.5
pandas==2.3.3
scikit-learn==1.8.0
scipy==1.16.3
```

### NLP/ML (🔄 INSTALLING)
```
transformers>=4.36.0
torch>=2.1.0
nltk>=3.8.1
textblob>=0.17.1
```

### Optional (For Production)
```
tensorflow>=2.15.0  # For advanced models
sentencepiece>=0.1.99  # For tokenization
accelerate>=0.25.0  # For GPU acceleration
```

## Installation Commands

### Quick Install (All at Once)
```bash
cd backend
.\venv\Scripts\pip.exe install numpy pandas scikit-learn scipy transformers torch nltk textblob
```

### Minimal Install (Just NLP)
```bash
.\venv\Scripts\pip.exe install transformers torch nltk textblob
```

### Full Install (Everything)
```bash
.\venv\Scripts\pip.exe install -r requirements.txt
```

## Testing Workflow

### 1. Pre-Test Checklist
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Internet connection (for model downloads)
- [ ] ~2GB free disk space

### 2. Quick Test First
```bash
python test_ml_quick.py
```

**Expected output:**
```
================================================================================
QUICK ML TEST - NLP FEATURES
================================================================================

[TEST 1] Testing imports...
✓ ML modules imported successfully

[TEST 2] Initializing NLP service...
  Downloading transformer models (~1.5GB)...
✓ NLP service initialized

[TEST 3] Testing sentiment analysis...
  POSITIVE text: "I feel amazing today!..."
    Result: positive (score: 0.85)
✓ Sentiment analysis working!

... (more tests)

🎉 ALL NLP TESTS PASSED!
```

### 3. Full Test Suite
```bash
python test_ml_complete.py
```

**This will:**
1. Generate dummy mood data (60-90 days)
2. Test all NLP features
3. Train LSTM model (5 epochs for speed)
4. Make predictions
5. Detect patterns
6. Test collaborative filtering
7. Run A/B test simulation

**Duration:** 10-15 minutes on CPU, 3-5 minutes on GPU

### 4. API Testing
```bash
# Terminal 1: Start server
python -m uvicorn app.main:app --reload

# Terminal 2: Run tests
curl "http://localhost:8000/api/v1/ml/health"
```

## Troubleshooting

### Issue: Model Download Fails
```
✗ NLP initialization failed: HTTPError
```

**Solution:**
```bash
# Set HuggingFace cache directory
set TRANSFORMERS_CACHE=C:\Users\nikki\.cache\huggingface

# Or use offline mode (models must be pre-downloaded)
set TRANSFORMERS_OFFLINE=1
```

### Issue: Out of Memory
```
✗ CUDA out of memory
```

**Solution:**
```python
# In test script or config:
config.nlp.use_gpu = False  # Use CPU instead
config.prediction.batch_size = 8  # Reduce batch size
```

### Issue: Import Errors
```
ModuleNotFoundError: No module named 'torch'
```

**Solution:**
```bash
# Verify installation
.\venv\Scripts\pip.exe list | findstr torch

# Reinstall if needed
.\venv\Scripts\pip.exe install torch --upgrade
```

### Issue: NLTK Data Not Found
```
LookupError: Resource 'punkt' not found
```

**Solution:**
```bash
python -c "import nltk; nltk.download('all')"
```

## Expected Test Results

### Quick Test (~5-10 minutes first run)
```
Tests passed: 4/4
✓ Sentiment Analysis
✓ Emotion Classification
✓ Crisis Detection
✓ Full Journal Analysis
```

### Comprehensive Test (~15 minutes)
```
Tests passed: 15/15
✓ 4 NLP tests
✓ 3 LSTM tests
✓ 3 Pattern detection tests
✓ 4 Collaborative filtering tests
✓ 1 A/B testing test

Success rate: 100%
```

## Performance Expectations

### NLP Analysis (per entry)
- **CPU:** ~700ms
- **GPU:** ~180ms

### LSTM Training (50 epochs, 60 days)
- **CPU:** ~2-3 minutes
- **GPU:** ~30-45 seconds

### Mood Prediction (7 days ahead)
- **After training:** ~100-200ms

### Model Download (First Run Only)
- **Sentiment model:** ~500MB, ~2-3 minutes
- **Emotion model:** ~300MB, ~1-2 minutes
- **Crisis model:** ~600MB, ~3-4 minutes
- **Total:** ~1.4GB, ~8-10 minutes

## Next Steps After Testing

### If All Tests Pass ✅
1. Create database migration: `alembic upgrade head`
2. Start backend server
3. Test API endpoints
4. Integrate with frontend
5. Deploy to production

### If Some Tests Fail ❌
1. Check error logs in console output
2. Verify all dependencies installed
3. Check internet connection (for model downloads)
4. Review troubleshooting section
5. Check system resources (RAM, disk space)

## Production Deployment

### Before Deployment
- [ ] All tests passing
- [ ] Database migrated
- [ ] Environment variables set
- [ ] Models pre-downloaded
- [ ] GPU configured (optional)
- [ ] Monitoring setup
- [ ] Crisis alert system configured

### Environment Variables
```bash
# Optional
ML_USE_GPU=true
ML_MODEL_PATH=./ml_models
ML_LSTM_EPOCHS=50
TRANSFORMERS_CACHE=/path/to/cache
```

### Model Pre-loading
```python
# In startup script
from app.ml.nlp_service import get_nlp_service
nlp = get_nlp_service()  # Pre-load models
```

## Support

### Logs
```bash
# Check application logs
tail -f logs/app.log

# Check ML-specific logs
tail -f logs/ml_service.log
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Resources
- **Documentation:** `backend/app/ml/README.md`
- **Quick Start:** `backend/app/ml/QUICKSTART.md`
- **Implementation Summary:** `ML_IMPLEMENTATION_SUMMARY.md`

---

**Status:** Ready for testing once dependencies are installed!
**Current Step:** Installing ML dependencies (transformers, torch)
**Next Step:** Run `python test_ml_quick.py`
