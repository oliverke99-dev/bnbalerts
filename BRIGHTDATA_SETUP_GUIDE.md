# BrightData Setup Guide - Getting Real Airbnb Data

This guide will walk you through setting up BrightData to scrape real Airbnb property data instead of mock data.

## Step 1: Get Your BrightData Account Credentials

### 1.1 Sign Up / Log In to BrightData
1. Go to [https://brightdata.com](https://brightdata.com)
2. Sign up for an account or log in if you already have one
3. You'll need a paid plan to access the Scraping Browser API

### 1.2 Find Your API Key
1. Once logged in, go to your **Dashboard**
2. Navigate to **Settings** → **API Tokens** (or similar section)
3. Look for your **API Token** or **API Key**
4. Copy this key - it should look something like: `ed692cdc-6205-4a00-abce-7a5adbf66438`

### 1.3 Find Your Dataset ID for Airbnb
1. In your BrightData dashboard, go to **Datasets** or **Data Collector**
2. Look for **Airbnb** dataset or create a new one
3. The Dataset ID typically looks like: `gd_l7q7dkf244hwjntr0`
4. Common Airbnb dataset IDs:
   - `gd_l7q7dkf244hwjntr0` (Airbnb Search Results)
   - `gd_lkq7dkf244hwjntr1` (Airbnb Property Details)

**Note:** If you don't see a dataset ID, you may need to:
- Create a new dataset collector for Airbnb
- Subscribe to the Airbnb dataset in the marketplace
- Contact BrightData support to enable Airbnb scraping

## Step 2: Configure Your Application

### 2.1 Update Your .env File
Add or update these lines in your `.env` file:

```bash
# Bright Data Configuration
BRIGHTDATA_API_KEY=your_actual_api_key_here
BRIGHTDATA_DATASET_ID=gd_l7q7dkf244hwjntr0
BRIGHTDATA_API_URL=https://api.brightdata.com/datasets/v3
BRIGHTDATA_TIMEOUT=300
```

**Replace `your_actual_api_key_here` with your actual API key from Step 1.2**

### 2.2 Verify Your Configuration
Your `.env` file should now have:
```bash
BRIGHTDATA_API_KEY=ed692cdc-6205-4a00-abce-7a5adbf66438  # Your real key
BRIGHTDATA_DATASET_ID=gd_l7q7dkf244hwjntr0              # Airbnb dataset
BRIGHTDATA_API_URL=https://api.brightdata.com/datasets/v3
BRIGHTDATA_TIMEOUT=300
```

## Step 3: Test Your Configuration

### 3.1 Run the Verification Script
```bash
python3 verify_brightdata.py
```

This will:
- Check if your API key is configured
- Verify the dataset ID
- Test a sample scraping request
- Show you if you're in MOCK or REAL mode

### 3.2 Restart Your Backend
After updating the `.env` file:
```bash
# Stop the current backend (Ctrl+C in the terminal)
# Then restart it:
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3.3 Check the Startup Logs
Look for this message in your terminal:
- ✅ **REAL MODE**: `"BrightData client initialized with API key and dataset: gd_l7q7dkf244hwjntr0"`
- ❌ **MOCK MODE**: `"BrightData client initialized in MOCK MODE (no API key configured)"`

## Step 4: Test Real Scraping

### 4.1 Try a Search in Your App
1. Go to your frontend: http://localhost:3000
2. Navigate to the Discover page
3. Paste an Airbnb search URL
4. Click "Search Properties"

### 4.2 What to Expect
**With Real Data:**
- Properties will have real names from Airbnb
- Real property IDs (8-digit numbers from Airbnb)
- Actual property images from Airbnb
- Real prices and availability
- Takes 5-30 seconds (actual scraping time)

**With Mock Data:**
- Generic names like "Cozy Studio Apartment with City Views"
- Random property IDs
- Placeholder images (placehold.co)
- Random prices
- Takes exactly 2 seconds

## Troubleshooting

### Issue: Still Seeing Mock Data After Setup

**Check 1: Verify API Key is Set**
```bash
# In your project directory
grep BRIGHTDATA_API_KEY .env
```
Should show your actual key, not empty or default value.

**Check 2: Check Backend Logs**
Look at your backend terminal for:
```
BrightData client initialized in MOCK MODE
```
This means the API key isn't being read properly.

**Check 3: Restart Backend**
Make sure you restarted the backend after updating `.env`:
```bash
# Kill the process and restart
lsof -ti:8000 | xargs kill -9 2>/dev/null; sleep 2; python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Issue: API Errors

**Error: "BrightData API returned status 401"**
- Your API key is invalid or expired
- Double-check the key in your BrightData dashboard
- Make sure there are no extra spaces in the `.env` file

**Error: "No snapshot_id returned"**
- Your dataset ID might be incorrect
- Verify the dataset ID in your BrightData dashboard
- Make sure you have access to the Airbnb dataset

**Error: "Polling for results timed out"**
- BrightData is taking longer than expected
- This is normal for large searches
- You can increase `BRIGHTDATA_TIMEOUT` in `.env` (default is 300 seconds)

### Issue: No Properties Returned

**Possible Causes:**
1. The Airbnb search URL has no results
2. BrightData rate limits (check your account usage)
3. Network connectivity issues
4. Dataset configuration issues

**Solutions:**
- Try a different Airbnb search URL with known results
- Check your BrightData account for usage limits
- Review BrightData dashboard for any alerts

## Quick Reference: .env Configuration

```bash
# Complete BrightData configuration
BRIGHTDATA_API_KEY=your_api_key_from_brightdata_dashboard
BRIGHTDATA_DATASET_ID=gd_l7q7dkf244hwjntr0
BRIGHTDATA_API_URL=https://api.brightdata.com/datasets/v3
BRIGHTDATA_TIMEOUT=300
```

## Need Help?

1. **Check BrightData Documentation**: [https://docs.brightdata.com](https://docs.brightdata.com)
2. **Contact BrightData Support**: Available in your dashboard
3. **Review Application Logs**: Check your backend terminal for detailed error messages
4. **Run Verification Script**: `python3 verify_brightdata.py` for diagnostic information

## Cost Considerations

- BrightData charges per request/data volume
- Mock mode is free and unlimited
- Monitor your usage in the BrightData dashboard
- Consider implementing caching for frequently searched properties
- Set appropriate rate limits in production