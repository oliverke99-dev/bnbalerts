# Business Model Pivot: Specific Property Monitoring

## Overview

**OLD MODEL:** Search for any available properties matching user criteria  
**NEW MODEL:** Monitor specific Airbnb properties for cancellation availability

## New User Journey

### 1. User Discovers Property
- User finds perfect Airbnb property: `https://www.airbnb.com/rooms/12345678`
- Property is booked for their desired dates (June 1-7, 2024)
- User wants to be notified if it becomes available

### 2. User Adds Property to Watch
- Goes to "Add Property" page (formerly "Discover")
- Pastes full Airbnb URL: `https://www.airbnb.com/rooms/12345678`
- Enters desired dates: June 1-7, 2024
- System fetches and displays property details:
  - Property name
  - Location
  - Price
  - Image
  - Current status (booked/available)

### 3. User Configures Monitoring
- Selects monitoring frequency:
  - Daily (free tier)
  - Hourly (standard tier)
  - Every 5 minutes (sniper tier)
- Adds to watchlist (max 5 properties)

### 4. System Monitors Property
- Checks property availability at selected frequency
- Only checks that ONE specific property
- Compares current availability vs desired dates

### 5. User Gets Notified
- SMS alert when property becomes available
- Deep link directly to property with dates pre-filled
- User can book immediately

## Technical Implementation

### Frontend Changes

#### 1. Rename "Discover" → "Add Property"
**File:** `frontend/app/dashboard/discover/page.tsx`

**Changes:**
- Remove search URL input
- Add single property URL input
- Add date picker for check-in/check-out
- Add property preview card after URL validation
- Show property details fetched from backend

**New UI Flow:**
```
┌─────────────────────────────────────┐
│  Add Property to Watch              │
├─────────────────────────────────────┤
│                                     │
│  Property URL:                      │
│  [https://airbnb.com/rooms/12345]  │
│                                     │
│  Check-in Date:  [June 1, 2024]    │
│  Check-out Date: [June 7, 2024]    │
│                                     │
│  [Fetch Property Details]           │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Property Preview            │   │
│  │ ┌─────┐                     │   │
│  │ │ IMG │ Luxury Beach House  │   │
│  │ └─────┘ Miami, FL           │   │
│  │         $250/night          │   │
│  │         Status: Booked      │   │
│  └─────────────────────────────┘   │
│                                     │
│  Monitoring Frequency:              │
│  ○ Daily  ○ Hourly  ○ Every 5 min  │
│                                     │
│  [Add to Watchlist]                 │
└─────────────────────────────────────┘
```

#### 2. Update Watchlist Display
**File:** `frontend/app/dashboard/watchlist/page.tsx`

**Changes:**
- Show property URL (clickable)
- Show monitoring frequency
- Show last checked time
- Show current status (booked/available)

### Backend Changes

#### 1. New API Endpoint: Fetch Property Details
**Endpoint:** `POST /api/v1/properties/fetch-details`

**Purpose:** Validate property URL and fetch current details

**Request:**
```json
{
  "propertyUrl": "https://www.airbnb.com/rooms/12345678",
  "checkIn": "2024-06-01",
  "checkOut": "2024-06-07"
}
```

**Response:**
```json
{
  "propertyId": "12345678",
  "propertyName": "Luxury Beach House",
  "location": "Miami, FL",
  "price": "$250",
  "imageUrl": "https://...",
  "currentStatus": "booked",
  "isAvailable": false
}
```

**Implementation:**
- Extract property ID from URL
- Scrape property page directly (simpler than search results)
- Check availability for specified dates
- Return property details + availability status

#### 2. Update Watch Creation
**Endpoint:** `POST /api/v1/watches` (existing, needs update)

**Changes:**
- Accept property URL instead of search URL
- Store property ID extracted from URL
- Validate property exists before creating watch

#### 3. Simplified Availability Checking
**File:** `app/services/availability_checker.py`

**Changes:**
- Check ONE specific property page
- No need to compare search results
- Just check if property is available for dates
- Much simpler and more reliable

**New Logic:**
```python
async def check_property_availability(
    property_url: str,
    check_in: date,
    check_out: date
) -> bool:
    """
    Check if specific property is available for dates.
    
    Returns:
        True if available, False if booked
    """
    # Navigate to property page with dates
    url_with_dates = f"{property_url}?checkin={check_in}&checkout={check_out}"
    
    # Scrape property page
    page_content = await scrape_property_page(url_with_dates)
    
    # Check for availability indicators
    if "Reserve" in page_content or "Book" in page_content:
        return True  # Available
    elif "Not available" in page_content or "Booked" in page_content:
        return False  # Booked
    else:
        return None  # Unknown
```

## Advantages of New Model

### 1. Simpler Scraping
- ✅ Only scrape ONE property page (not search results)
- ✅ Property pages are more stable than search
- ✅ Easier to detect availability
- ✅ Less likely to be blocked

### 2. Better User Experience
- ✅ Users know exactly what they're monitoring
- ✅ No confusion about which property matched
- ✅ Direct link to exact property
- ✅ Clear status updates

### 3. More Reliable
- ✅ Property pages change less than search results
- ✅ Availability is clearly indicated on property page
- ✅ Fewer edge cases to handle
- ✅ Easier to maintain

### 4. Cost Effective
- ✅ Only 1 request per check (not 2 for comparison)
- ✅ Simpler scraping = cheaper API costs
- ✅ Can use cheaper scraping services

## Migration Plan

### Phase 1: Backend Updates (1-2 days)
1. Create `fetch-details` endpoint
2. Update availability checker for single property
3. Update watch creation to accept property URLs
4. Test with mock data

### Phase 2: Frontend Updates (1-2 days)
1. Rename Discover → Add Property
2. Update UI for single property input
3. Add property preview component
4. Update watchlist display
5. Test end-to-end flow

### Phase 3: Testing (1 day)
1. Test with real Airbnb URLs
2. Verify availability detection
3. Test notification flow
4. Load testing with multiple properties

### Phase 4: Deploy (1 day)
1. Update documentation
2. Deploy backend changes
3. Deploy frontend changes
4. Monitor for issues

## API Cost Comparison

### OLD MODEL (Search Comparison)
- 2 requests per check (no dates + with dates)
- 100 properties × 12 checks/hour × 2 requests = 2,400 requests/hour
- ~$180/day with ScraperAPI

### NEW MODEL (Single Property)
- 1 request per check (just the property page)
- 100 properties × 12 checks/hour × 1 request = 1,200 requests/hour
- ~$90/day with ScraperAPI
- **50% cost reduction!**

## Success Metrics

### User Metrics
- Number of properties added to watchlist
- Average monitoring duration
- Notification click-through rate
- Successful bookings after notification

### Technical Metrics
- Availability check success rate (target: >95%)
- Average check duration (target: <5 seconds)
- False positive rate (target: <1%)
- System uptime (target: 99.9%)

## Next Steps

1. ✅ Get user confirmation on requirements
2. ⏳ Implement backend changes
3. ⏳ Update frontend UI
4. ⏳ Test with real Airbnb URLs
5. ⏳ Deploy to production

## Questions Answered

1. **Property Input:** ✅ User pastes full Airbnb URL
2. **Discovery Page:** ✅ Convert to "Add Property to Watch"
3. **Validation:** ✅ Fetch and display property details
4. **Watchlist Limit:** ✅ Still max 5 properties
5. **Check Frequency:** ✅ Daily/Hourly/Every 5 minutes (3 tiers)

---

**Status:** Ready to implement  
**Estimated Time:** 3-5 days  
**Priority:** High  
**Complexity:** Medium (simpler than original!)