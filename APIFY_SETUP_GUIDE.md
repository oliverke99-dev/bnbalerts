# Apify Setup Guide - Getting Real Airbnb Data

This guide will walk you through setting up Apify to scrape real Airbnb property data instead of mock data.

## Step 1: Get Your Apify Account Credentials

### 1.1 Sign Up / Log In to Apify
1. Go to [https://apify.com](https://apify.com)
2. Sign up for a free account or log in if you already have one
3. Navigate to **Settings** → **Integrations** in your dashboard

### 1.2 Get Your API Token
1. In the Integrations page, find your **Personal API Token**
2. Copy this token - you'll need it for the `.env` file
3. Keep this token secure - it provides access to your Apify account

### 1.3 Choose an Airbnb Scraper Actor
The default actor we use is `dtrungtin/airbnb-scraper`, which is a popular and reliable Airbnb scraper.

**Alternative actors you can use:**
- `maxcopell/airbnb-scraper`
- `dtrungtin/airbnb-scraper` (recommended)
- Any custom actor you've created

## Step 2: Configure Your Environment

### 2.1 Update Your `.env` File

Open your `.env` file and update the Apify configuration:

```bash
# Apify Configuration
APIFY_API_TOKEN=your_actual_api_token_here
APIFY_ACTOR_ID=dtrungtin/airbnb-scraper
APIFY_API_URL=https://api.apify.com/v2
APIFY_TIMEOUT=300
```

### 2.2 Example Configuration

```bash
APIFY_API_TOKEN=apify_api_AbCdEfGhIjKlMnOpQrStUvWxYz123456  # Your real token
APIFY_ACTOR_ID=dtrungtin/airbnb-scraper                      # Airbnb scraper actor
APIFY_API_URL=https://api.apify.com/v2
APIFY_TIMEOUT=300
```

**Important Notes:**
- The API token starts with `apify_api_`
- Don't include quotes around the values
- Make sure there are no trailing spaces

## Step 3: Restart Your Backend

After updating the `.env` file:

```bash
# Stop the backend (Ctrl+C in the terminal)
# Then restart it
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Step 4: Verify It's Working

### 4.1 Check the Startup Logs

Look for this message in your terminal:
- ✅ **REAL MODE**: `"Apify client initialized with API token and actor: dtrungtin/airbnb-scraper"`
- ❌ **MOCK MODE**: `"Apify client initialized in MOCK MODE (no API token configured)"`

### 4.2 Test the Discovery Endpoint

Try searching for properties:

```bash
curl -X POST http://localhost:8000/api/v1/properties/discover \
  -H "Content-Type: application/json" \
  -d '{
    "airbnbUrl": "https://www.airbnb.com/s/San-Francisco--CA/homes?checkin=2024-06-01&checkout=2024-06-07&adults=2"
  }'
```

If you see real property data (not mock data), it's working! 🎉

## Troubleshooting

### Still Seeing Mock Data?

**Check your `.env` file:**
```bash
# In your project directory
grep APIFY_API_TOKEN .env
```

**Check the logs:**
If you see:
```
Apify client initialized in MOCK MODE
```

Then your API token is not being read correctly. Make sure:
1. The `.env` file is in the project root directory
2. There are no typos in `APIFY_API_TOKEN`
3. You've restarted the backend after updating `.env`

### Common Errors

**Error: "Apify API returned status 401"**
- Your API token is invalid or expired
- Double-check the token in your Apify dashboard
- Make sure there are no extra spaces in the `.env` file

**Error: "Actor not found"**
- Your actor ID might be incorrect
- Verify the actor exists: https://apify.com/dtrungtin/airbnb-scraper
- Make sure you have access to the actor (some are private)

**Error: "Polling for results timed out"**
- Apify is taking longer than expected
- This is normal for large searches
- You can increase `APIFY_TIMEOUT` in `.env` (default is 300 seconds)

**Error: "No properties found"**
This could mean:
1. The Airbnb search URL has no results
2. Apify rate limits (check your account usage)
3. Network connectivity issues

**Solutions:**
- Try a different Airbnb search URL with known results
- Check your Apify account for usage limits
- Review Apify dashboard for any alerts

## Complete Configuration Example

```bash
# Complete Apify configuration
APIFY_API_TOKEN=apify_api_YourActualTokenHere123456789
APIFY_ACTOR_ID=dtrungtin/airbnb-scraper
APIFY_API_URL=https://api.apify.com/v2
APIFY_TIMEOUT=300
```

## Additional Resources

1. **Check Apify Documentation**: [https://docs.apify.com](https://docs.apify.com)
2. **Airbnb Scraper Actor**: [https://apify.com/dtrungtin/airbnb-scraper](https://apify.com/dtrungtin/airbnb-scraper)
3. **Contact Apify Support**: Available in your dashboard
4. **Review Application Logs**: Check your backend terminal for detailed error messages

## Pricing & Usage

- Apify offers a **free tier** with limited usage
- Paid plans start at $49/month for more requests
- Monitor your usage in the Apify dashboard
- Consider implementing caching for frequently searched properties

## Switching Between Mock and Real Mode

**To use REAL data:**
- Set `APIFY_API_TOKEN` in your `.env` file

**To use MOCK data (for development):**
- Remove or comment out `APIFY_API_TOKEN` in your `.env` file
- Or set it to an empty string: `APIFY_API_TOKEN=`

Mock mode is useful for:
- Development without API costs
- Testing the application flow
- Demos and presentations