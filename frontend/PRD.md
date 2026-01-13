# PRODUCT REQUIREMENTS DOCUMENT

## EXECUTIVE SUMMARY

**Product Name:** BnBAlerts

**Product Vision:** BnBAlerts is a high-speed cancellation alert service that monitors specific Short Term Rental (STR) inventory to capture last-minute availability in high-demand markets. The platform automates the tedious "search and refresh" process, allowing travelers to secure "unicorn" properties the moment cancellations occur.

**Core Purpose:** Solves the problem of travelers who cannot find suitable STR properties for non-flexible dates (events, conferences, family gatherings) by continuously monitoring booked properties and instantly alerting users when cancellations create availability.

**Target Users:** 
- Event attendees (F1 races, festivals, playoffs) with fixed dates
- Group organizers needing large properties (3-5 bedrooms) in specific locations
- Business travelers with non-negotiable conference/meeting windows

**Key MVP Features:**
- **Property Discovery & Watchlist** - User-Generated Content (search, select, manage watched properties)
- **Scan Configuration** - Configuration (frequency tiers, date ranges, notification preferences)
- **Cancellation Monitoring Engine** - System Data (automated scanning with anti-bot measures)
- **SMS Notifications** - Communication (instant alerts with deep links)
- **User Account Management** - System/Configuration (registration, phone verification, profile)

**Platform:** Web application (responsive, accessible via browser on all devices)

**Complexity Assessment:** Complex
- **State Management:** Backend-required (distributed scanning engine, scheduled jobs, webhook processing)
- **External Integrations:** Airbnb API scraping (via proxy service), SMS provider (Twilio/Telnyx), A2P 10DLC registration - these reduce implementation complexity
- **Business Logic:** Complex (anti-bot evasion, verify-retry logic, distributed scanning across frequency tiers, scan lifecycle management)

**MVP Success Criteria:**
- Users complete full workflow: paste search URL → view unavailable properties → add to watchlist → receive SMS alert
- Scanning engine successfully monitors properties without being blocked (>95% success rate)
- SMS notifications delivered within 60 seconds of verified availability
- All CRUD operations for watchlist management functional
- Responsive design works on mobile/tablet/desktop

---

## 1. USERS & PERSONAS

**Primary Persona: "Sarah the Event Hound"**
- **Context:** 32-year-old marketing professional attending F1 Miami Grand Prix with 3 friends. Booked flights 6 months ago, but all 4-bedroom properties within 5 miles of the track are fully booked.
- **Goals:** Secure a property that fits her group size and location requirements the instant a cancellation occurs, without manually refreshing Airbnb every hour.
- **Pain Points:** Manually checking availability is time-consuming and ineffective. By the time she sees a cancellation, it's already re-booked. Misses opportunities because she's at work or asleep.

**Secondary Persona: "Marcus the Group Organizer"**
- **Context:** 45-year-old father organizing annual family reunion for 12 people. Needs 5-bedroom property in specific beach town for fixed week in July.
- **Goals:** Monitor multiple "perfect fit" properties and book immediately when one becomes available.
- **Pain Points:** Large group properties are scarce. Can't afford to miss cancellations. Needs instant notification to act before others.

---

## 2. FUNCTIONAL REQUIREMENTS

### 2.1 Core MVP Features (Priority 0)

**FR-001: User Account & Authentication**
- **Description:** Secure registration with email/password, phone verification via OTP, session management
- **Entity Type:** System/Configuration
- **Operations:** Register, Login, View profile, Edit profile (name, email, phone), Logout, Delete account
- **Key Rules:** Phone verification required before creating watches. TCPA-compliant SMS consent during registration.
- **Acceptance:** Users can register, verify phone, login, and manage account settings

**FR-002: Property Discovery from Search Criteria**
- **Description:** User pastes Airbnb search URL; system scrapes unavailable properties matching criteria and displays up to 20 results
- **Entity Type:** System Data
- **Operations:** Submit search URL, View results list with property details and deep links, Refresh search
- **Key Rules:** Search URL must include check-in/check-out dates. System extracts location, dates, guest count, filters from URL.
- **Acceptance:** Users paste search URL and see list of unavailable properties with images, names, prices, and Airbnb deep links

**FR-003: Watchlist Management**
- **Description:** Users select up to 5 properties from discovery results to monitor for cancellations
- **Entity Type:** User-Generated Content
- **Operations:** Create watch (add property), View watchlist, Edit watch (change dates/preferences), Delete watch, List all active watches
- **Key Rules:** Maximum 5 concurrent watches per user. Each watch includes property ID, check-in/out dates, scan frequency tier, partial match toggle.
- **Acceptance:** Users can add properties to watchlist, view all watches, modify settings, and remove watches

**FR-004: Scan Configuration**
- **Description:** Configure monitoring frequency and notification preferences for each watch
- **Entity Type:** Configuration
- **Operations:** Select frequency tier (Daily/Hourly/5-Minute), Toggle partial match alerts, View current settings, Edit settings, Reset to defaults
- **Key Rules:** Free tier = Daily scans. Standard tier = Hourly scans. Sniper tier = 5-minute scans. Partial match toggle allows alerts for partial date availability.
- **Acceptance:** Users can select scan frequency, enable/disable partial match alerts, and modify settings per watch

**FR-005: Cancellation Monitoring Engine**
- **Description:** Automated scanning system that checks property availability at configured intervals using anti-bot measures
- **Entity Type:** System Data
- **Operations:** View scan status, View scan history/logs, Export scan logs
- **Key Rules:** Verify-retry logic (30-second re-check before alerting). Auto-terminate scans at 11:59 PM on check-in date. Rotate proxies and user-agents per scan.
- **Acceptance:** System successfully scans properties without blocking, verifies availability twice, and auto-terminates expired scans

**FR-006: SMS Notification System**
- **Description:** Instant SMS alerts with deep links when verified availability detected
- **Entity Type:** Communication
- **Operations:** Create notification (system-triggered), View notification history, Reply STOP to unsubscribe
- **Key Rules:** Include property name, dates, and deep link with dates pre-filled. Deliver within 60 seconds of verified availability. Support STOP command to kill specific watch.
- **Acceptance:** Users receive SMS within 60 seconds of availability, can click deep link to Airbnb, and can reply STOP to cancel watch

---

## 3. USER WORKFLOWS

### 3.1 Primary Workflow: Property Watch Setup & Alert

**Trigger:** User cannot find available property on Airbnb for their specific dates
**Outcome:** User receives instant SMS alert when monitored property becomes available

**Steps:**
1. User registers account with email/password and verifies phone number via OTP
2. User pastes Airbnb search URL (with dates, location, filters) into BnBAlerts discovery form
3. System scrapes Airbnb API, displays up to 20 unavailable properties matching criteria with images and details
4. User reviews properties, clicks "Add to Watchlist" on up to 5 properties, selects scan frequency tier (Daily/Hourly/5-Minute) and partial match preference
5. System initiates scanning engine with verify-retry logic, rotating proxies, and scheduled jobs based on frequency tier
6. When availability detected, system re-verifies after 30 seconds, then sends SMS with deep link to property page with dates pre-filled
7. User clicks SMS link, opens Airbnb app/website, completes booking within 60 seconds

### 3.2 Key Supporting Workflows

**Edit Watch Settings:** User opens watchlist → clicks edit on watch → modifies frequency tier or partial match toggle → saves → sees updated settings

**Delete Watch:** User opens watchlist → clicks delete on watch → confirms deletion → watch removed and scanning stopped

**View Scan History:** User navigates to watch detail → views scan log with timestamps and status → exports log as CSV

**Stop via SMS:** User receives alert → replies "STOP" → system immediately terminates that specific watch and confirms via SMS

**Refresh Property Search:** User returns to discovery page → clicks refresh → system re-scrapes Airbnb with same criteria → displays updated results

---

## 4. BUSINESS RULES

### 4.1 Entity Lifecycle Rules

| Entity | Type | Who Creates | Who Edits | Who Deletes | Delete Action |
|--------|------|-------------|-----------|-------------|---------------|
| User Account | System/Config | Self-registration | Owner | Owner | Hard delete + cascade watches |
| Watch | User-Generated | Account owner | Owner | Owner or System (auto-expire) | Soft delete (archive 30 days) |
| Scan Log | System Data | System | None | None | Auto-purge after 90 days |
| SMS Notification | Communication | System | None | None | Retain 30 days for audit |
| Search Result | System Data | System | None | System | Expire after 24 hours |

### 4.2 Data Validation Rules

| Entity | Required Fields | Key Constraints |
|--------|-----------------|-----------------|
| User | email, password, phone | Email unique, phone verified via OTP, password min 8 chars |
| Watch | propertyId, checkIn, checkOut, userId, frequencyTier | Max 5 active per user, checkIn >= today, checkOut > checkIn |
| Scan Log | watchId, timestamp, status, result | Status: success/blocked/error, result: available/unavailable/partial |
| SMS Notification | watchId, phone, message, deepLink | Phone E.164 format, message max 160 chars |

### 4.3 Access & Process Rules

- Users can only view/edit/delete their own watches and account data
- Free tier users limited to Daily scan frequency (1 scan per 24 hours per watch)
- Standard tier users limited to Hourly scans (1 scan per hour per watch)
- Sniper tier users get 5-minute scans (1 scan per 5 minutes per watch)
- Scans auto-terminate at 11:59 PM on check-in date (no manual extension)
- Verify-retry logic: System must detect availability, wait 30 seconds, re-check, then alert (prevents false positives)
- SMS STOP command immediately kills associated watch and sends confirmation
- Maximum 5 concurrent active watches per user (can delete and create new ones)
- Partial match toggle: If enabled, alerts sent when any portion of date range becomes available (not just full dates)

---

## 5. DATA REQUIREMENTS

### 5.1 Core Entities

**User**
- **Type:** System/Configuration | **Storage:** Backend database
- **Key Fields:** id, email, passwordHash, phone, phoneVerified, smsConsent, createdAt, updatedAt, lastLoginAt
- **Relationships:** has many Watches, has many Notifications
- **Lifecycle:** Full CRUD with phone verification, account deletion cascades to watches

**Watch**
- **Type:** User-Generated Content | **Storage:** Backend database
- **Key Fields:** id, userId, propertyId, propertyName, propertyUrl, checkInDate, checkOutDate, frequencyTier (daily/hourly/5min), partialMatchEnabled, status (active/paused/expired), createdAt, updatedAt, expiresAt
- **Relationships:** belongs to User, has many ScanLogs, has many Notifications
- **Lifecycle:** Full CRUD + auto-archive on expiration + manual STOP command

**ScanLog**
- **Type:** System Data | **Storage:** Backend database
- **Key Fields:** id, watchId, scannedAt, status (success/blocked/error), result (available/unavailable/partial), proxyUsed, userAgent, responseTime, errorMessage
- **Relationships:** belongs to Watch
- **Lifecycle:** View + Export only, auto-purge after 90 days

**Notification**
- **Type:** Communication | **Storage:** Backend database
- **Key Fields:** id, watchId, userId, phone, message, deepLink, sentAt, deliveryStatus (sent/delivered/failed), clickedAt
- **Relationships:** belongs to Watch, belongs to User
- **Lifecycle:** Create + View only, retain 30 days for audit

**SearchResult**
- **Type:** System Data | **Storage:** Backend cache (Redis)
- **Key Fields:** searchId, userId, searchUrl, properties (array of property objects), scrapedAt, expiresAt
- **Relationships:** belongs to User (temporary)
- **Lifecycle:** View only, auto-expire after 24 hours

### 5.2 Data Storage Strategy

- **Primary Storage:** Backend database (PostgreSQL/MySQL) for persistent data
- **Cache Layer:** Redis for search results (24-hour TTL) and scan job queues
- **Capacity:** Database scales with user growth; Redis cache limited to active searches
- **Persistence:** All user data, watches, and logs persist indefinitely (with auto-purge rules)
- **Audit Fields:** All entities include createdAt, updatedAt, createdBy (userId), updatedBy (userId or system)

---

## 6. INTEGRATION REQUIREMENTS

**Airbnb API Scraping Service (via Bright Data or similar):**
- **Purpose:** Query Airbnb's internal APIs to retrieve unavailable property listings matching search criteria
- **Type:** Backend HTTP calls via residential proxy rotation
- **Data Exchange:** Sends search URL with dates/filters, receives JSON array of property objects (id, name, price, images, availability)
- **Trigger:** On user search submission and during scheduled scan jobs
- **Error Handling:** Retry with different proxy on 403/429 errors, log failures, alert user if persistent blocking

**SMS Provider (Twilio/Telnyx):**
- **Purpose:** Send SMS notifications with deep links when availability detected
- **Type:** Backend API calls
- **Data Exchange:** Sends phone number, message body, deep link; receives delivery status webhooks
- **Trigger:** After verify-retry logic confirms availability
- **Error Handling:** Retry failed sends up to 3 times, log delivery failures, mark notification as failed

**A2P 10DLC Campaign Registry:**
- **Purpose:** Register SMS campaigns to ensure deliverability and avoid carrier spam filtering
- **Type:** One-time registration via SMS provider dashboard
- **Data Exchange:** Submit business info, use case, sample messages; receive campaign approval
- **Trigger:** During initial platform setup before production launch
- **Error Handling:** Manual review if rejected, adjust messaging to comply with carrier guidelines

---

## 7. VIEWS & NAVIGATION

### 7.1 Primary Views

**Landing Page** (`/`) - Hero section explaining service, value proposition, CTA to sign up, pricing tiers display

**Registration/Login** (`/register`, `/login`) - Email/password forms, phone verification OTP input, TCPA consent checkbox

**Dashboard** (`/dashboard`) - Active watches list with status indicators, quick stats (scans run, alerts sent), CTA to create new watch

**Property Discovery** (`/discover`) - Search URL input form, results grid showing 20 unavailable properties with images/details, "Add to Watchlist" buttons

**Watchlist** (`/watchlist`) - Table of active watches with property name, dates, frequency tier, status, edit/delete actions

**Watch Detail** (`/watchlist/:id`) - Full watch info, scan history log, notification history, edit settings form, delete button

**Settings** (`/settings`) - Profile (name, email, phone), notification preferences, tier selection (Free/Standard/Sniper), account deletion

### 7.2 Navigation Structure

**Main Nav:** Dashboard | Discover | Watchlist | Settings | User Menu (profile, logout)
**Default Landing:** Dashboard (after login) or Landing Page (logged out)
**Mobile:** Hamburger menu, responsive grid layouts, touch-optimized buttons

---

## 8. MVP SCOPE & CONSTRAINTS

### 8.1 MVP Success Definition

The MVP is successful when:
- ✅ Users complete full workflow: register → verify phone → paste search URL → view unavailable properties → add to watchlist → receive SMS alert
- ✅ Scanning engine successfully monitors properties with >95% success rate (not blocked by Airbnb)
- ✅ Verify-retry logic prevents false positives (<2% false positive rate)
- ✅ SMS notifications delivered within 60 seconds of verified availability
- ✅ All watchlist CRUD operations functional
- ✅ Scans auto-terminate at check-in date
- ✅ STOP command immediately kills watch
- ✅ Responsive design works on mobile/tablet/desktop

### 8.2 In Scope for MVP

Core features included:
- FR-001: User Account & Authentication (registration, phone verification, login, profile management)
- FR-002: Property Discovery from Search Criteria (scrape unavailable properties, display results)
- FR-003: Watchlist Management (add/edit/delete watches, 5-watch limit)
- FR-004: Scan Configuration (frequency tiers, partial match toggle)
- FR-005: Cancellation Monitoring Engine (scheduled scans, anti-bot measures, verify-retry logic, auto-termination)
- FR-006: SMS Notification System (instant alerts, deep links, STOP command)

### 8.3 Technical Constraints

- **Data Storage:** Backend database (PostgreSQL/MySQL) with Redis cache for search results and job queues
- **Concurrent Users:** Expected 100-500 users during MVP testing phase
- **Performance:** Dashboard loads <2s, property discovery results <5s, SMS delivery <60s from availability detection
- **Browser Support:** Chrome, Firefox, Safari, Edge (last 2 versions)
- **Mobile:** Responsive design, iOS/Android browser support, SMS deep links open native Airbnb app if installed
- **Offline:** Not supported (requires backend connectivity for scanning and notifications)
- **Scanning Frequency:** Daily (Free), Hourly (Standard), 5-Minute (Sniper) - enforced via scheduled job intervals
- **Anti-Bot Measures:** Residential proxy rotation (Bright Data), headless browser emulation (Playwright/Puppeteer), varied user-agents, randomized scan timing within frequency window

### 8.4 Known Limitations

**For MVP:**
- No payment processing - tier selection is cosmetic (all users can access all tiers for testing)
- Deep links may not pre-fill dates if Airbnb restricts URL parameters (fallback to property page)
- Search results limited to 20 properties (Airbnb API pagination not implemented)
- No multi-device sync (user must login on each device)
- No email notifications (SMS only)
- No watch sharing or collaboration features
- Scan logs retained for 90 days only (no long-term analytics)

**Future Enhancements:**
- V2 will add Stripe payment processing to enforce tier limits
- Expand to VRBO, Booking.com property monitoring
- Email notification option for users without SMS
- Advanced filters (price range, amenities, reviews)
- Watch templates for recurring trips
- Mobile app with push notifications

---

## 9. ASSUMPTIONS & DECISIONS

### 9.1 Platform Decisions

- **Type:** Full-stack web application (frontend + backend + scheduled jobs)
- **Storage:** Backend database (PostgreSQL) + Redis cache for ephemeral data
- **Auth:** Backend-managed with JWT tokens, phone verification via SMS OTP
- **Scanning:** Backend scheduled jobs (cron/queue system) with distributed workers

### 9.2 Entity Lifecycle Decisions

**User Account:** Full CRUD + account deletion
- **Reason:** Users need full control over personal data; deletion cascades to watches for privacy compliance

**Watch:** Full CRUD + auto-archive on expiration
- **Reason:** User-generated content requiring full lifecycle management; soft delete preserves audit trail

**Scan Log:** View + Export only
- **Reason:** System-generated audit data; no user editing needed; auto-purge after 90 days for storage management

**Notification:** Create + View only
- **Reason:** Communication records for audit/compliance; immutable once sent; 30-day retention

**Search Result:** View only (ephemeral)
- **Reason:** Temporary cache data; expires after 24 hours; no persistence needed

### 9.3 Key Assumptions

1. **Airbnb API scraping is technically feasible with anti-bot measures**
   - Reasoning: User confirmed functional scraping engine is hard requirement. Residential proxies and headless browsers are proven methods for bypassing bot detection. Budget allocated for proxy service (Bright Data ~$500/month).

2. **Users will tolerate 30-second verify-retry delay for accuracy**
   - Reasoning: False positives erode trust. A 30-second re-check before alerting ensures availability is real, preventing user frustration from "ghost" listings. Total latency still under 60 seconds.

3. **SMS is the primary notification channel (no email in MVP)**
   - Reasoning: Speed is critical for booking "unicorn" properties. SMS delivers instantly and has higher open rates than email. Deep links work seamlessly from SMS to mobile apps.

4. **5-watch limit is sufficient for MVP validation**
   - Reasoning: Most users have 1-3 "perfect" properties in mind. 5 watches allow testing without overwhelming the scanning infrastructure. Can increase limit post-MVP based on usage data.

5. **Free tier selection without payment validates upgrade intent**
   - Reasoning: User confirmed no payment processing in MVP. Allowing tier selection tests user willingness to "upgrade" and provides data on feature value without Stripe integration complexity.

### 9.4 Clarification Q&A Summary

**Q:** How do users select specific properties to watch if Airbnb hides booked properties?
**A:** Use scraping service to query Airbnb APIs for unavailable properties, display up to 20 results, allow user to select up to 5 for watchlist.
**Decision:** Built FR-002 (Property Discovery) to scrape and display unavailable properties before watchlist creation.

**Q:** Is functional scraping engine required for MVP, or can we simulate with mock data?
**A:** Functional scraping engine is hard requirement before launch.
**Decision:** Prioritized anti-bot infrastructure (proxies, headless browsers) as core technical requirement. No simulation/mock data approach.

**Q:** Should deep links pre-fill dates in Airbnb app, or is standard property link sufficient?
**A:** Ideally include dates, but standard link acceptable if too difficult.
**Decision:** Attempt date pre-fill via URL parameters; fallback to property page if Airbnb restricts. Document limitation in Section 8.4.

**Q:** Should MVP include payment processing (Stripe) to enforce tier limits?
**A:** Allow users to select tiers freely without charging to test upgrade flow.
**Decision:** Tier selection is cosmetic in MVP. All users access all features. Payment integration deferred to V2.

---

**PRD Complete - Ready for Development**