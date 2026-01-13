# Browser-Based Scraping Setup Guide

## Overview

This guide explains how to set up and use the browser-based Airbnb scraper, which eliminates the need for BrightData or other external scraping services.

## Installation

### 1. Install Playwright

```bash
# Install the Python package
pip install playwright

# Install browser binaries (Chromium)
playwright install chromium
```

### 2. Verify Installation

```bash
# Test that Playwright is installed correctly
python3 -c "from playwright.sync_api import sync_playwright; print('Playwright installed successfully!')"
```

## How It Works

The browser-based scraper uses **Playwright** to automate a real Chromium browser:

1. **Launches a headless browser** - Runs Chrome in the background
2. **Navigates to Airbnb** - Opens search pages like a real user
3. **Extracts property data** - Scrapes listing information from the page
4. **Compares results** - Identifies booked properties by comparing searches with/without dates

### Advantages

✅ **No API keys required** - Works without BrightData or other services  
✅ **Real browser behavior** - Less likely to be blocked  
✅ **Full control** - You control the scraping logic  
✅ **Cost-effective** - No per-request charges  

### Disadvantages

⚠️ **Slower** - Takes 10-30 seconds per search (vs 2-5 seconds with BrightData)  
⚠️ **Resource intensive** - Requires more CPU/memory  
⚠️ **Maintenance** - May need updates if Airbnb changes their HTML  
⚠️ **Rate limiting** - Airbnb may block excessive requests  

## API Endpoints

### Browser-Based Booking Detection

**Endpoint:** `POST /api/v1/properties/detect-bookings-browser`

**Description:** Detect booked properties using direct browser scraping (no BrightData required).

**Request Body:**
```json
{
  "location": "Austin, TX",
  "checkIn": "2024-06-01",
  "checkOut": "2024-06-07",
  "adults": 2,
  "children": 0,
  "maxResults": 50
}
```

**Response:** Same format as other booking detection endpoints.

## Usage Examples

### Using cURL

```bash
# Get JWT token first
TOKEN="your_jwt_token_here"

# Detect bookings with browser scraping
curl -X POST http://localhost:8000/api/v1/properties/detect-bookings-browser \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Austin, TX",
    "checkIn": "2024-06-01",
    "checkOut": "2024-06-07",
    "adults": 2,
    "children": 0,
    "maxResults": 30
  }'
```

### Using Python

```python
import requests
from datetime import date, timedelta

API_BASE = "http://localhost:8000/api/v1"
TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Calculate dates
check_in = date.today() + timedelta(days=30)
check_out = check_in + timedelta(days=7)

# Detect bookings with browser scraping
response = requests.post(
    f"{API_BASE}/properties/detect-bookings-browser",
    headers=headers,
    json={
        "location": "Austin, TX",
        "checkIn": check_in.isoformat(),
        "checkOut": check_out.isoformat(),
        "adults": 2,
        "children": 0,
        "maxResults": 30
    }
)

result = response.json()
print(f"Found {result['booked_count']} booked properties")
print(f"Found {result['available_count']} available properties")

for prop in result['booked_properties']:
    print(f"Booked: {prop['propertyName']} - {prop['price']}")
```

### Using JavaScript/TypeScript

```typescript
const API_BASE = 'http://localhost:8000/api/v1';
const TOKEN = 'your_jwt_token_here';

async function detectBookingsBrowser(location: string, checkIn: string, checkOut: string) {
  const response = await fetch(`${API_BASE}/properties/detect-bookings-browser`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      location,
      checkIn,
      checkOut,
      adults: 2,
      children: 0,
      maxResults: 30,
    }),
  });

  const result = await response.json();
  console.log(`Found ${result.booked_count} booked properties`);
  
  return result;
}

// Usage
detectBookingsBrowser('Austin, TX', '2024-06-01', '2024-06-07')
  .then(result => {
    result.booked_properties.forEach(prop => {
      console.log(`Booked: ${prop.propertyName} - ${prop.price}`);
    });
  });
```

## Performance Optimization

### 1. Reduce maxResults

Lower values are faster:
```json
{
  "maxResults": 20  // Faster than 50
}
```

### 2. Use Caching

Cache results for 5-10 minutes to avoid repeated scraping:
```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def get_cached_results(location, check_in, check_out):
    # Results cached for repeated calls
    return detect_bookings_browser(location, check_in, check_out)
```

### 3. Run in Background

For long-running operations, use background tasks:
```python
from fastapi import BackgroundTasks

@app.post("/detect-async")
async def detect_async(request: Request, background_tasks: BackgroundTasks):
    background_tasks.add_task(detect_bookings_browser, request.location, ...)
    return {"status": "processing"}
```

## Troubleshooting

### Error: "Playwright not installed"

**Solution:**
```bash
pip install playwright
playwright install chromium
```

### Error: "Browser launch failed"

**Possible causes:**
1. Missing system dependencies
2. Insufficient permissions
3. Headless mode issues

**Solutions:**
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2

# For macOS, ensure Xcode Command Line Tools are installed
xcode-select --install
```

### Slow Performance

**Tips:**
1. Reduce `maxResults` to 20-30
2. Use headless mode (default)
3. Disable images: Add to browser launch options
4. Run on a server with good internet connection

### Rate Limiting / Blocked

**Symptoms:**
- 403 errors
- CAPTCHAs
- Empty results

**Solutions:**
1. Add delays between requests
2. Rotate user agents
3. Use residential proxies (if needed)
4. Reduce request frequency

## Comparison: Browser vs BrightData

| Feature | Browser Scraping | BrightData |
|---------|-----------------|------------|
| **Setup** | Install Playwright | API key required |
| **Cost** | Free | Pay per request |
| **Speed** | 10-30 seconds | 2-5 seconds |
| **Reliability** | Good | Excellent |
| **Maintenance** | May need updates | Maintained by provider |
| **Rate Limits** | Self-managed | Handled by service |
| **Best For** | Development, low volume | Production, high volume |

## When to Use Each Method

### Use Browser Scraping When:
- ✅ You're in development/testing
- ✅ You have low request volume (< 100/day)
- ✅ You want to avoid external dependencies
- ✅ Cost is a primary concern

### Use BrightData When:
- ✅ You're in production
- ✅ You have high request volume (> 100/day)
- ✅ Speed is critical
- ✅ You need guaranteed uptime

## Configuration

### Environment Variables

No additional environment variables required! The browser scraper works out of the box after installing Playwright.

### Optional: Custom Browser Settings

You can customize browser behavior in [`app/integrations/browser_scraper.py`](app/integrations/browser_scraper.py:1):

```python
# Example: Run in non-headless mode for debugging
self.browser = await self.playwright.chromium.launch(
    headless=False,  # Show browser window
    slow_mo=1000,    # Slow down by 1 second per action
)
```

## Testing

### Manual Test

```bash
# Test browser scraping directly
python3 -c "
import asyncio
from datetime import date, timedelta
from app.services.browser_booking_detector import BrowserBookingDetector

async def test():
    detector = BrowserBookingDetector()
    result = await detector.detect_booked_properties(
        location='Austin, TX',
        check_in=date.today() + timedelta(days=30),
        check_out=date.today() + timedelta(days=37),
        adults=2,
        max_results=10
    )
    print(f'Found {result[\"booked_count\"]} booked properties')
    print(f'Found {result[\"available_count\"]} available properties')

asyncio.run(test())
"
```

## Security Considerations

1. **User Agent Rotation**: The scraper uses realistic user agents
2. **Rate Limiting**: Implement delays between requests
3. **IP Rotation**: Consider using proxies for high volume
4. **Error Handling**: Gracefully handle blocks and errors

## Support

For issues:
1. Check Playwright installation: `playwright --version`
2. Verify browser binaries: `playwright install --dry-run chromium`
3. Review logs for specific errors
4. Test with a simple Playwright script first

## Additional Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [Airbnb Terms of Service](https://www.airbnb.com/terms)
- [Web Scraping Best Practices](https://www.scrapehero.com/web-scraping-best-practices/)