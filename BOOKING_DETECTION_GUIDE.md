# Airbnb Booking Detection Service

## Overview

The Booking Detection Service identifies properties on Airbnb that are already booked for specific dates by comparing search results with and without date filters. This provides visibility into properties that don't appear in standard date-filtered searches because they're unavailable.

## How It Works

### Strategy

The service uses a comparison-based approach:

1. **Search WITHOUT dates** - Retrieves all properties in a location regardless of availability
2. **Search WITH specific dates** - Retrieves only properties available for those dates
3. **Compare results** - Properties in the first search but not the second are identified as booked

### Why This Works

Airbnb's UI and API hide booked properties when you search with specific dates. By running both searches and comparing the property IDs, we can identify which properties exist but are unavailable (booked) for your desired dates.

## API Endpoints

### 1. Detect Bookings from URL

**Endpoint:** `POST /api/v1/properties/detect-bookings`

**Description:** Detect booked properties by providing an Airbnb search URL with dates.

**Request Body:**
```json
{
  "searchUrl": "https://www.airbnb.com/s/Austin--TX/homes?checkin=2024-06-01&checkout=2024-06-07&adults=2",
  "maxResults": 50
}
```

**Response:**
```json
{
  "booked_properties": [
    {
      "propertyId": "12345678",
      "propertyName": "Luxury Beach House",
      "propertyUrl": "https://www.airbnb.com/rooms/12345678",
      "location": "Austin, TX",
      "price": "$250",
      "imageUrl": "https://example.com/image.jpg",
      "guests": 4,
      "status": "booked",
      "availability": "unavailable",
      "checkInDate": "2024-06-01",
      "checkOutDate": "2024-06-07"
    }
  ],
  "available_properties": [
    {
      "propertyId": "87654321",
      "propertyName": "Downtown Apartment",
      "propertyUrl": "https://www.airbnb.com/rooms/87654321",
      "location": "Austin, TX",
      "price": "$150",
      "imageUrl": "https://example.com/image2.jpg",
      "guests": 2,
      "status": "available",
      "availability": "available",
      "checkInDate": "2024-06-01",
      "checkOutDate": "2024-06-07"
    }
  ],
  "total_properties": 25,
  "booked_count": 15,
  "available_count": 10,
  "search_metadata": {
    "location": "Austin, TX",
    "checkIn": "2024-06-01",
    "checkOut": "2024-06-07",
    "guests": 2,
    "adults": 2,
    "children": 0
  }
}
```

### 2. Detect Bookings Direct

**Endpoint:** `POST /api/v1/properties/detect-bookings-direct`

**Description:** Detect booked properties by providing search parameters directly.

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

**Response:** Same format as detect-bookings endpoint.

## Usage Examples

### Using cURL

```bash
# Get JWT token first
TOKEN="your_jwt_token_here"

# Detect bookings from URL
curl -X POST http://localhost:8000/api/v1/properties/detect-bookings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "searchUrl": "https://www.airbnb.com/s/Austin--TX/homes?checkin=2024-06-01&checkout=2024-06-07&adults=2",
    "maxResults": 50
  }'

# Detect bookings with direct parameters
curl -X POST http://localhost:8000/api/v1/properties/detect-bookings-direct \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Austin, TX",
    "checkIn": "2024-06-01",
    "checkOut": "2024-06-07",
    "adults": 2,
    "children": 0,
    "maxResults": 50
  }'
```

### Using Python

```python
import requests
from datetime import date, timedelta

# Configuration
API_BASE = "http://localhost:8000/api/v1"
TOKEN = "your_jwt_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Method 1: Using URL
response = requests.post(
    f"{API_BASE}/properties/detect-bookings",
    headers=headers,
    json={
        "searchUrl": "https://www.airbnb.com/s/Austin--TX/homes?checkin=2024-06-01&checkout=2024-06-07&adults=2",
        "maxResults": 50
    }
)

result = response.json()
print(f"Found {result['booked_count']} booked properties")
print(f"Found {result['available_count']} available properties")

# Method 2: Using direct parameters
check_in = date.today() + timedelta(days=30)
check_out = check_in + timedelta(days=7)

response = requests.post(
    f"{API_BASE}/properties/detect-bookings-direct",
    headers=headers,
    json={
        "location": "Austin, TX",
        "checkIn": check_in.isoformat(),
        "checkOut": check_out.isoformat(),
        "adults": 2,
        "children": 0,
        "maxResults": 50
    }
)

result = response.json()
for prop in result['booked_properties']:
    print(f"Booked: {prop['propertyName']} - {prop['price']}")
```

### Using JavaScript/TypeScript

```typescript
const API_BASE = 'http://localhost:8000/api/v1';
const TOKEN = 'your_jwt_token_here';

async function detectBookings(searchUrl: string) {
  const response = await fetch(`${API_BASE}/properties/detect-bookings`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      searchUrl,
      maxResults: 50,
    }),
  });

  const result = await response.json();
  console.log(`Found ${result.booked_count} booked properties`);
  console.log(`Found ${result.available_count} available properties`);
  
  return result;
}

// Usage
const url = 'https://www.airbnb.com/s/Austin--TX/homes?checkin=2024-06-01&checkout=2024-06-07&adults=2';
detectBookings(url).then(result => {
  result.booked_properties.forEach(prop => {
    console.log(`Booked: ${prop.propertyName} - ${prop.price}`);
  });
});
```

## Architecture

### Components

1. **BookingDetector Service** (`app/services/booking_detector.py`)
   - Core logic for comparing search results
   - Handles both URL-based and direct parameter searches
   - Manages BrightData client for scraping

2. **API Endpoints** (`app/api/properties.py`)
   - `/detect-bookings` - URL-based detection
   - `/detect-bookings-direct` - Parameter-based detection
   - Both require JWT authentication

3. **Models** (`app/models/booking.py`)
   - `BookingDetectionRequest` - URL-based request
   - `BookingDetectionDirectRequest` - Parameter-based request
   - `BookingDetectionResponse` - Unified response format
   - `PropertyBookingStatus` - Individual property status

### Data Flow

```
User Request
    ↓
API Endpoint (JWT Auth)
    ↓
BookingDetector Service
    ↓
┌─────────────────────────────────┐
│  Search WITHOUT dates           │
│  (via BrightData)               │
│  → Returns ALL properties       │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Search WITH dates              │
│  (via BrightData)               │
│  → Returns AVAILABLE properties │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Compare Results                │
│  → Identify booked properties   │
│  → Enrich with metadata         │
└─────────────────────────────────┘
    ↓
Response to User
```

## Configuration

### Environment Variables

The booking detection service uses the existing BrightData configuration:

```bash
# BrightData Configuration (required for real scraping)
BRIGHTDATA_API_KEY=your_api_key_here
BRIGHTDATA_DATASET_ID=gd_l7q7dkf244hwjntr0
BRIGHTDATA_API_URL=https://api.brightdata.com/datasets/v3
BRIGHTDATA_TIMEOUT=300
```

### Mock Mode

If `BRIGHTDATA_API_KEY` is not set, the service operates in mock mode, generating realistic test data. This is useful for development and testing.

## Performance Considerations

### Timing

- Each detection requires **2 scraping operations** (with and without dates)
- Average response time: 5-15 seconds (depending on BrightData)
- Mock mode response time: ~2 seconds

### Rate Limits

- Respects BrightData rate limits
- Recommended: Max 10 requests per minute per user
- Consider implementing caching for repeated searches

### Optimization Tips

1. **Adjust maxResults**: Lower values (20-30) are faster
2. **Cache results**: Store results for 5-10 minutes
3. **Batch processing**: Queue multiple searches if needed
4. **Use mock mode**: For development and testing

## Error Handling

### Common Errors

1. **Invalid URL** (400)
   ```json
   {
     "detail": "Invalid request: Location is required in the search URL"
   }
   ```

2. **Missing Dates** (400)
   ```json
   {
     "detail": "Invalid request: Check-in and check-out dates are required"
   }
   ```

3. **Scraping Failure** (500)
   ```json
   {
     "detail": "Failed to detect bookings: BrightData API error"
   }
   ```

4. **Authentication** (401)
   ```json
   {
     "detail": "Not authenticated"
   }
   ```

### Retry Strategy

The service automatically retries failed scraping operations:
- Max 3 attempts per search
- Exponential backoff between retries
- Falls back to mock mode if BrightData fails

## Testing

### Manual Testing

1. **Start the backend:**
   ```bash
   python3 -m uvicorn main:app --reload --port 8000
   ```

2. **Get authentication token:**
   ```bash
   # Login to get token
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "password123"}'
   ```

3. **Test booking detection:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/properties/detect-bookings-direct \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "location": "Austin, TX",
       "checkIn": "2024-06-01",
       "checkOut": "2024-06-07",
       "adults": 2,
       "maxResults": 20
     }'
   ```

### Expected Results (Mock Mode)

In mock mode, you should see:
- 10-15 total properties
- Mix of booked and available properties
- Realistic property data with names, prices, images
- Proper status flags (`booked` vs `available`)

## Use Cases

### 1. Cancellation Monitoring

Monitor specific properties to detect when they become available:

```python
# Check if a specific property is booked
result = detect_bookings_direct(
    location="Miami Beach, FL",
    check_in="2024-07-01",
    check_out="2024-07-07"
)

target_property_id = "12345678"
is_booked = any(
    prop['propertyId'] == target_property_id 
    for prop in result['booked_properties']
)

if is_booked:
    print("Property is booked - add to watchlist")
else:
    print("Property is available - book now!")
```

### 2. Market Analysis

Analyze booking rates for a location:

```python
result = detect_bookings_direct(
    location="Austin, TX",
    check_in="2024-06-01",
    check_out="2024-06-07",
    max_results=100
)

booking_rate = result['booked_count'] / result['total_properties']
print(f"Booking rate: {booking_rate:.1%}")
```

### 3. Price Comparison

Compare prices of booked vs available properties:

```python
result = detect_bookings_direct(...)

booked_prices = [
    int(prop['price'].replace('$', '')) 
    for prop in result['booked_properties']
]
available_prices = [
    int(prop['price'].replace('$', '')) 
    for prop in result['available_properties']
]

print(f"Avg booked price: ${sum(booked_prices)/len(booked_prices):.0f}")
print(f"Avg available price: ${sum(available_prices)/len(available_prices):.0f}")
```

## Limitations

1. **Scraping Dependency**: Relies on BrightData for Airbnb scraping
2. **Rate Limits**: Subject to BrightData API rate limits
3. **Data Freshness**: Results are point-in-time snapshots
4. **Property Limit**: Maximum 100 properties per search
5. **Location Specificity**: Requires valid Airbnb location format

## Future Enhancements

- [ ] Add caching layer for repeated searches
- [ ] Implement webhook notifications for booking changes
- [ ] Add historical booking data tracking
- [ ] Support for multiple locations in single request
- [ ] Price trend analysis over time
- [ ] Integration with watchlist for automatic monitoring

## Support

For issues or questions:
- Check logs: `tail -f logs/app.log`
- Review BrightData status: Check `BRIGHTDATA_API_KEY` configuration
- Test in mock mode: Remove `BRIGHTDATA_API_KEY` temporarily
- Contact support: Include request/response details and timestamps