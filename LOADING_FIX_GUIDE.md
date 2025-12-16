# Firefly Loading Issue - Quick Fix Guide

## Problem
Pages showing continuous loading with no data displayed.

## Root Causes
1. Database not initialized with tables
2. No user account exists to login
3. Missing TensorFlow dependency
4. Frontend trying to fetch data before authentication

## Quick Fix (5 minutes)

### Step 1: Install Missing Dependencies
```bash
cd C:\users\nikki\firefly\backend
.\venv\Scripts\activate
pip install tensorflow
```

### Step 2: Initialize Database
```bash
# Still in backend directory with venv activated
python init_database.py
```

This will:
- Create all database tables
- Create demo user: `demo@firefly.com` / `Demo123!`
- Seed 5 sample interventions

### Step 3: Restart Application
```bash
# Close any running instances first (Ctrl+C in both terminals)

# Terminal 1: Backend
cd C:\users\nikki\firefly\backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd C:\users\nikki\firefly\frontend
npm run dev
```

### Step 4: Login
1. Go to http://localhost:5173
2. Click "Login" or go to http://localhost:5173/login
3. Use credentials:
   - **Email**: demo@firefly.com
   - **Password**: Demo123!

## Expected Behavior After Fix

### Dashboard Page
- Shows "Welcome back, Demo User"
- Displays mood chart (will be empty until you create check-ins)
- Shows recent check-ins section
- Quick check-in button available

### Check-in Page
- Mood slider (1-10)
- Energy, anxiety, stress sliders
- Journal text area
- Submit button works

### Insights Page
- Will show "Not enough data" messages initially
- Requires minimum data:
  - 7 days for basic patterns
  - 21 days for predictions
  - 90 days for seasonal patterns

### Analytics Page
- Shows placeholder charts
- Message: "Start tracking to see analytics"

## Create Some Test Data

To populate the dashboard with data:

```bash
cd C:\users\nikki\firefly\backend
python create_test_data.py
```

(If this file doesn't exist, you can create check-ins manually through the UI)

## Manual Check-in Creation
1. Go to Check-in page
2. Set mood: 7
3. Set energy: 6
4. Add journal text: "Feeling good today, had a productive morning"
5. Click Submit
6. Repeat for 5-7 days with different values

## Verify Backend is Working

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"healthy",...}`

### Test 2: API Docs
Open: http://localhost:8000/docs
You should see Swagger API documentation

### Test 3: ML Health
```bash
curl http://localhost:8000/api/v1/ml/health
```
Expected: `{"status":"healthy","services":{...}}`

## Common Issues & Solutions

### Issue: "Connection refused" or "Network error"
**Solution**: Backend not running
```bash
cd C:\users\nikki\firefly\backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

### Issue: "401 Unauthorized" errors
**Solution**: Not logged in or token expired
- Logout and login again
- Clear browser storage (F12 → Application → Local Storage → Clear)

### Issue: "Database connection failed"
**Solution**: PostgreSQL not running
```bash
# Check PostgreSQL service
sc query postgresql-x64-15

# Start if not running
net start postgresql-x64-15
```

### Issue: Pages still loading after login
**Solution**: Check browser console (F12)
- Look for red errors
- Common errors:
  - 404: Endpoint not found (expected for some ML endpoints initially)
  - 500: Server error (check backend terminal for stack trace)
  - CORS: Should be fixed, but check CORS_ORIGINS in .env

### Issue: "Module not found" errors in backend
**Solution**: Install missing dependencies
```bash
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Development Mode vs Production

Currently in **Development Mode**:
- Debug logging enabled
- Hot reload on code changes
- CORS allows localhost
- Demo credentials work

For production deployment:
- Change SECRET_KEY in .env
- Update CORS_ORIGINS
- Disable DEBUG
- Use strong passwords
- Enable HTTPS

## Next Steps After Fix

1. **Create check-ins**: Add 7+ days of mood data
2. **Try interventions**: Browse intervention library
3. **Train ML model**: After 21 days of data, train LSTM model
4. **View predictions**: Get 7-day mood forecasts
5. **Explore patterns**: See weekly/monthly patterns after 90 days

## Still Having Issues?

### Enable Debug Logging
In `backend/app/main.py`, set:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Check Browser Console
Press F12, go to Console tab, look for errors

### Check Backend Logs
Look for errors in terminal running uvicorn

### Database Issues
```bash
# Check database exists
psql -U postgres -l | findstr firefly

# If not, create it
psql -U postgres -c "CREATE DATABASE firefly_db;"
```

## Support
- Check logs in backend terminal
- Browser console (F12)
- GitHub Issues: https://github.com/Nikkinach/firefly/issues

---

**TL;DR**: Run `python init_database.py` in backend, login with `demo@firefly.com` / `Demo123!`
