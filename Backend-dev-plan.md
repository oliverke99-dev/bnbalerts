# BACKEND DEVELOPMENT PLAN - BnBAlerts

## 1️⃣ EXECUTIVE SUMMARY

**What Will Be Built:**
- FastAPI backend (Python 3.13, async) for BnBAlerts cancellation monitoring service
- MongoDB Atlas database using Motor driver and Pydantic v2 models
- JWT-based authentication with phone verification
- Property discovery via Airbnb URL scraping
- Watchlist management (max 5 concurrent watches per user)
- Automated scanning engine with frequency tiers (Daily/Hourly/5-Minute)
- SMS notification system via Twilio
- RESTful API at `/api/v1/*` base path

**Key Constraints:**
- Python 3.13 runtime with FastAPI async
- MongoDB Atlas only (no local instance)
- No Docker containers
- Single Git branch `main` only
- Manual testing required after every task via frontend UI
- Background tasks synchronous by default (use `BackgroundTasks` only if necessary)

**Sprint Structure:**
- **S0:** Environment setup and frontend connection
- **S1:** Authentication (signup, login, logout, phone verification)
- **S2:** Property discovery (Airbnb URL scraping)
- **S3:** Watchlist management (CRUD operations)
- **S4:** Scanning engine (scheduled jobs with frequency tiers)
- **S5:** SMS notifications (Twilio integration)

---

## 2️⃣ IN-SCOPE & SUCCESS CRITERIA

**In-Scope Features:**
- User registration with email/password
- Phone verification via SMS OTP
- JWT-based session management
- Property discovery from Airbnb search URLs
- Watchlist CRUD (create, read, update, delete watches)
- Scan frequency configuration (daily/hourly/5-minute tiers)
- Automated property scanning with anti-bot measures
- SMS alerts with deep links when availability detected
- User profile management
- Notification preferences

**Success Criteria:**
- All frontend features functional end-to-end
- Users can complete full workflow: register → verify phone → discover properties → add to watchlist → receive SMS alert
- All task-level manual tests pass via UI
- Each sprint's code pushed to `main` after verification
- Scanning engine achieves >95% success rate (not blocked)
- SMS notifications delivered within 60 seconds

---

## 3️⃣ API DESIGN

**Base Path:** `/api/v1`

**Error Envelope:** `{ "error": "message" }`

### Authentication Endpoints

**POST `/api/v1/auth/signup`**
- Purpose: Register new user with email, password, phone
- Request: `{ "email": "user@example.com", "password": "pass123", "phone": "+15551234567" }`
- Response: `{ "user": { "id": "...", "email": "...", "phone": "...", "phoneVerified": false }, "message": "OTP sent to phone" }`
- Validation: Email unique, password min 8 chars, phone E.164 format

**POST `/api/v1/auth/verify-phone`**
- Purpose: Verify phone number with OTP code
- Request: `{ "userId": "...", "code": "123456" }`
- Response: `{ "success": true, "token": "jwt_token_here" }`
- Validation: Code must match stored OTP, expires after 10 minutes

**POST `/api/v1/auth/login`**
- Purpose: Authenticate user and return JWT
- Request: `{ "email": "user@example.com", "password": "pass123" }`
- Response: `{ "token": "jwt_token_here", "user": { "id": "...", "email": "...", "phoneVerified": true } }`
- Validation: Credentials must match, phone must be verified

**POST `/api/v1/auth/logout`**
- Purpose: Invalidate current session (client-side token removal)
- Request: Headers with `Authorization: Bearer <token>`
- Response: `{ "message": "Logged out successfully" }`

**GET `/api/v1/auth/me`**
- Purpose: Get current user profile
- Request: Headers with `Authorization: Bearer <token>`
- Response: `{ "id": "...", "email": "...", "phone": "...", "phoneVerified": true, "tier": "free" }`

### Property Discovery Endpoints

**POST `/api/v1/properties/discover`**
- Purpose: Scrape Airbnb for unavailable properties matching search URL
- Request: `{ "searchUrl": "https://www.airbnb.com/s/Austin--TX/homes?checkin=..." }`
- Response: `{ "properties": [{ "id": "...", "name": "...", "location": "...", "price": "...", "imageUrl": "...", "dates": "...", "guests": 4 }], "count": 8 }`
- Validation: URL must be valid Airbnb search URL with dates

### Watchlist Endpoints

**POST `/api/v1/watches`**
- Purpose: Create new watch for property
- Request: `{ "propertyId": "...", "propertyName": "...", "propertyUrl": "...", "checkInDate": "2024-10-12", "checkOutDate": "2024-10-15", "frequency": "hourly", "partialMatch": false }`
- Response: `{ "watch": { "id": "...", "status": "active", "createdAt": "..." } }`
- Validation: Max 5 active watches per user, checkIn >= today, checkOut > checkIn

**GET `/api/v1/watches`**
- Purpose: List all watches for current user
- Request: Headers with `Authorization: Bearer <token>`
- Response: `{ "watches": [{ "id": "...", "propertyName": "...", "status": "active", "frequency": "hourly", "lastChecked": "..." }] }`

**GET `/api/v1/watches/:id`**
- Purpose: Get single watch details with scan history
- Request: Headers with `Authorization: Bearer <token>`
- Response: `{ "watch": { "id": "...", "propertyName": "...", "status": "active" }, "scanLogs": [{ "scannedAt": "...", "result": "unavailable" }] }`

**PATCH `/api/v1/watches/:id`**
- Purpose: Update watch settings (frequency, status)
- Request: `{ "frequency": "daily", "status": "paused" }`
- Response: `{ "watch": { "id": "...", "frequency": "daily", "status": "paused" } }`

**DELETE `/api/v1/watches/:id`**
- Purpose: Delete watch and stop scanning
- Request: Headers with `Authorization: Bearer <token>`
- Response: `{ "message": "Watch deleted successfully" }`

### User Settings Endpoints

**PATCH `/api/v1/users/profile`**
- Purpose: Update user profile (name, phone)
- Request: `{ "name": "John Doe", "phone": "+15551234567" }`
- Response: `{ "user": { "id": "...", "name": "John Doe", "email": "...", "phone": "..." } }`

**PATCH `/api/v1/users/notifications`**
- Purpose: Update notification preferences
- Request: `{ "smsEnabled": true, "emailEnabled": false }`
- Response: `{ "preferences": { "smsEnabled": true, "emailEnabled": false } }`

### Dashboard Stats

**GET `/api/v1/stats/dashboard`**
- Purpose: Get dashboard statistics
- Request: Headers with `Authorization: Bearer <token>`
- Response: `{ "activeWatches": 3, "scansToday": 142, "alertsSent": 12, "recentActivity": [...] }`

### Health Check

**GET `/healthz`**
- Purpose: Health check with MongoDB connection status
- Response: `{ "status": "healthy", "database": "connected", "timestamp": "..." }`

---

## 4️⃣ DATA MODEL (MongoDB Atlas)

### Collection: `users`

**Fields:**
- `_id`: ObjectId (auto-generated)
- `email`: string (required, unique, indexed)
- `passwordHash`: string (required, Argon2 hashed)
- `phone`: string (required, E.164 format)
- `phoneVerified`: boolean (default: false)
- `phoneOtp`: string (nullable, expires after 10 min)
- `phoneOtpExpiry`: datetime (nullable)
- `name`: string (optional)
- `tier`: string (enum: "free", "standard", "sniper", default: "free")
- `smsEnabled`: boolean (default: true)
- `emailEnabled`: boolean (default: false)
- `createdAt`: datetime (auto)
- `updatedAt`: datetime (auto)

**Example Document:**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "email": "user@example.com",
  "passwordHash": "$argon2id$v=19$m=65536...",
  "phone": "+15551234567",
  "phoneVerified": true,
  "phoneOtp": null,
  "phoneOtpExpiry": null,
  "name": "John Doe",
  "tier": "free",
  "smsEnabled": true,
  "emailEnabled": false,
  "createdAt": "2024-01-15T10:30:00Z",
  "updatedAt": "2024-01-15T10:30:00Z"
}
```

### Collection: `watches`

**Fields:**
- `_id`: ObjectId (auto-generated)
- `userId`: ObjectId (required, indexed, references users)
- `propertyId`: string (required, Airbnb property ID)
- `propertyName`: string (required)
- `propertyUrl`: string (required)
- `location`: string (required)
- `checkInDate`: date (required)
- `checkOutDate`: date (required)
- `guests`: integer (required)
- `price`: string (required)
- `frequency`: string (enum: "daily", "hourly", "sniper", default: "daily")
- `partialMatch`: boolean (default: false)
- `status`: string (enum: "active", "paused", "expired", default: "active")
- `lastScannedAt`: datetime (nullable)
- `nextScanAt`: datetime (nullable)
- `expiresAt`: datetime (auto-calculated: checkInDate at 23:59:59)
- `createdAt`: datetime (auto)
- `updatedAt`: datetime (auto)

**Example Document:**
```json
{
  "_id": "507f1f77bcf86cd799439012",
  "userId": "507f1f77bcf86cd799439011",
  "propertyId": "12345678",
  "propertyName": "Luxury Beach House",
  "propertyUrl": "https://www.airbnb.com/rooms/12345678",
  "location": "Miami, FL",
  "checkInDate": "2024-10-12",
  "checkOutDate": "2024-10-15",
  "guests": 4,
  "price": "$250/night",
  "frequency": "hourly",
  "partialMatch": false,
  "status": "active",
  "lastScannedAt": "2024-01-15T14:30:00Z",
  "nextScanAt": "2024-01-15T15:30:00Z",
  "expiresAt": "2024-10-12T23:59:59Z",
  "createdAt": "2024-01-15T10:00:00Z",
  "updatedAt": "2024-01-15T14:30:00Z"
}
```

### Collection: `scan_logs`

**Fields:**
- `_id`: ObjectId (auto-generated)
- `watchId`: ObjectId (required, indexed, references watches)
- `scannedAt`: datetime (required, indexed)
- `status`: string (enum: "success", "blocked", "error")
- `result`: string (enum: "available", "unavailable", "partial")
- `proxyUsed`: string (nullable)
- `userAgent`: string (nullable)
- `responseTime`: integer (milliseconds)
- `errorMessage`: string (nullable)

**Example Document:**
```json
{
  "_id": "507f1f77bcf86cd799439013",
  "watchId": "507f1f77bcf86cd799439012",
  "scannedAt": "2024-01-15T14:30:00Z",
  "status": "success",
  "result": "unavailable",
  "proxyUsed": "proxy-us-east-1.example.com",
  "userAgent": "Mozilla/5.0...",
  "responseTime": 1250,
  "errorMessage": null
}
```

### Collection: `notifications`

**Fields:**
- `_id`: ObjectId (auto-generated)
- `watchId`: ObjectId (required, references watches)
- `userId`: ObjectId (required, references users)
- `phone`: string (required, E.164 format)
- `message`: string (required, max 160 chars)
- `deepLink`: string (required)
- `sentAt`: datetime (required)
- `deliveryStatus`: string (enum: "sent", "delivered", "failed")
- `twilioSid`: string (nullable)
- `clickedAt`: datetime (nullable)

**Example Document:**
```json
{
  "_id": "507f1f77bcf86cd799439014",
  "watchId": "507f1f77bcf86cd799439012",
  "userId": "507f1f77bcf86cd799439011",
  "phone": "+15551234567",
  "message": "🎉 Luxury Beach House is now available for Oct 12-15! Book now: https://bnb.al/xyz",
  "deepLink": "https://www.airbnb.com/rooms/12345678?checkin=2024-10-12&checkout=2024-10-15",
  "sentAt": "2024-01-15T14:31:00Z",
  "deliveryStatus": "delivered",
  "twilioSid": "SM1234567890abcdef",
  "clickedAt": null
}
```

---

## 5️⃣ FRONTEND AUDIT & FEATURE MAP

### Landing Page (`/`)
- **Route:** `frontend/app/page.tsx`
- **Purpose:** Marketing page with hero, features, how-it-works
- **Data Needed:** None (static content)
- **Backend Endpoints:** None
- **Auth Required:** No

### Registration Page (`/register`)
- **Route:** `frontend/app/register/page.tsx`
- **Purpose:** User signup with email, password, phone + OTP verification
- **Data Needed:** User registration, OTP verification
- **Backend Endpoints:** `POST /api/v1/auth/signup`, `POST /api/v1/auth/verify-phone`
- **Auth Required:** No
- **Notes:** Two-step process (details → verify), uses dummy OTP "123456" in frontend

### Login Page (`/login`)
- **Route:** `frontend/app/login/page.tsx`
- **Purpose:** User authentication
- **Data Needed:** Login credentials validation
- **Backend Endpoints:** `POST /api/v1/auth/login`
- **Auth Required:** No

### Dashboard (`/dashboard`)
- **Route:** `frontend/app/dashboard/page.tsx`
- **Purpose:** Overview with stats (active watches, scans today, alerts sent), recent activity feed
- **Data Needed:** User stats, active watches preview, recent activity logs
- **Backend Endpoints:** `GET /api/v1/watches`, `GET /api/v1/stats/dashboard`
- **Auth Required:** Yes
- **Notes:** Shows 3 active watches preview, stats cards, activity timeline

### Discover Properties (`/dashboard/discover`)
- **Route:** `frontend/app/dashboard/discover/page.tsx`
- **Purpose:** Paste Airbnb URL, scrape unavailable properties, select up to 5 to watch
- **Data Needed:** Property discovery results from Airbnb URL
- **Backend Endpoints:** `POST /api/v1/properties/discover`, `POST /api/v1/watches` (bulk create)
- **Auth Required:** Yes
- **Notes:** Parses Airbnb URL for location/dates/guests, displays 4-8 properties, enforces 5-watch limit

### Watchlist (`/dashboard/watchlist`)
- **Route:** `frontend/app/dashboard/watchlist/page.tsx`
- **Purpose:** Manage active watches (view, edit frequency, pause/resume, delete)
- **Data Needed:** All user watches with status and last scan time
- **Backend Endpoints:** `GET /api/v1/watches`, `PATCH /api/v1/watches/:id`, `DELETE /api/v1/watches/:id`
- **Auth Required:** Yes
- **Notes:** Shows watch count (X/5), frequency toggle (daily/hourly/sniper), pause/play buttons

### Settings (`/dashboard/settings`)
- **Route:** `frontend/app/dashboard/settings/page.tsx`
- **Purpose:** Update profile (name, phone), notification preferences (SMS/email toggles)
- **Data Needed:** User profile, notification settings
- **Backend Endpoints:** `GET /api/v1/auth/me`, `PATCH /api/v1/users/profile`, `PATCH /api/v1/users/notifications`
- **Auth Required:** Yes
- **Notes:** Email field disabled (cannot change), phone editable, SMS/email toggles

---

## 6️⃣ CONFIGURATION & ENV VARS

**Required Environment Variables:**

- `APP_ENV` — Environment (development, production)
- `PORT` — HTTP port (default: 8000)
- `MONGODB_URI` — MongoDB Atlas connection string
- `JWT_SECRET` — Secret key for JWT signing (min 32 chars)
- `JWT_EXPIRES_IN` — JWT expiration in seconds (default: 86400)
- `CORS_ORIGINS` — Comma-separated allowed origins
- `TWILIO_ACCOUNT_SID` — Twilio account SID
- `TWILIO_AUTH_TOKEN` — Twilio auth token
- `TWILIO_PHONE_NUMBER` — Twilio phone number (E.164 format)
- `BRIGHTDATA_API_KEY` — Bright Data proxy service API key
- `BRIGHTDATA_PROXY_URL` — Bright Data proxy endpoint

**Example `.env` file:**
```
APP_ENV=development
PORT=8000
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/bnbalerts
JWT_SECRET=your-super-secret-jwt-key-min-32-chars
JWT_EXPIRES_IN=86400
CORS_ORIGINS=http://localhost:3000
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+15551234567
BRIGHTDATA_API_KEY=your_brightdata_key
BRIGHTDATA_PROXY_URL=https://proxy.brightdata.com
```

---

## 7️⃣ BACKGROUND WORK

### Scanning Engine

**Trigger:** Scheduled jobs based on watch frequency tier
- Daily: Run once per day at random time between 8 AM - 8 PM user local time
- Hourly: Run every hour on the hour
- Sniper: Run every 5 minutes

**Purpose:** Check property availability on Airbnb via scraping service

**Process:**
1. Query all active watches where `nextScanAt <= now()`
2. For each watch, make HTTP request to Bright Data proxy with Airbnb property URL
3. Parse response to determine availability (available/unavailable/partial)
4. If available, trigger verify-retry logic (wait 30 seconds, re-check)
5. If still available after retry, create notification and send SMS
6. Log scan result to `scan_logs` collection
7. Update watch `lastScannedAt` and calculate `nextScanAt` based on frequency
8. Auto-expire watches where `expiresAt <= now()` (set status to "expired")

**Idempotency:** Each scan creates unique log entry; duplicate availability alerts prevented by checking last notification timestamp

**UI Feedback:** Frontend polls `GET /api/v1/watches` to see updated `lastScannedAt` timestamps

### SMS Notification Delivery

**Trigger:** Availability detected after verify-retry logic

**Purpose:** Send instant SMS alert with deep link to property

**Process:**
1. Create notification record in `notifications` collection
2. Call Twilio API to send SMS with message and deep link
3. Update notification `deliveryStatus` based on Twilio response
4. Handle Twilio webhooks for delivery status updates

**Idempotency:** Check if notification already sent for this watch in last 24 hours to prevent duplicates

**UI Feedback:** Notification history visible in watch detail view (future enhancement)

---

## 8️⃣ INTEGRATIONS

### Airbnb Scraping via Bright Data

**Purpose:** Query Airbnb's internal APIs to retrieve property availability

**Flow:**
1. Backend receives Airbnb search URL from frontend
2. Extract search parameters (location, dates, guests, filters)
3. Make HTTP request to Bright Data proxy with Airbnb API endpoint
4. Bright Data rotates residential proxies and user-agents to avoid blocking
5. Parse JSON response containing property listings
6. Filter for unavailable properties only
7. Return up to 20 properties to frontend

**Error Handling:**
- 403/429 errors: Retry with different proxy (max 3 attempts)
- Persistent blocking: Log error, return empty results with error message
- Network timeout: Retry once, then fail gracefully

**Extra ENV Vars:** `BRIGHTDATA_API_KEY`, `BRIGHTDATA_PROXY_URL`

### Twilio SMS Provider

**Purpose:** Send SMS notifications with deep links

**Flow:**
1. Backend detects availability after verify-retry
2. Format SMS message (max 160 chars): "🎉 [Property Name] is now available for [Dates]! Book now: [Short Link]"
3. Call Twilio API: `POST https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json`
4. Include `To`, `From`, `Body` parameters
5. Store Twilio message SID in notification record
6. Handle delivery status webhooks at `POST /api/v1/webhooks/twilio`

**Error Handling:**
- Failed send: Retry up to 3 times with exponential backoff
- Invalid phone number: Mark notification as failed, log error
- Rate limit: Queue message for retry after cooldown period

**Extra ENV Vars:** `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`

---

## 9️⃣ TESTING STRATEGY (Manual via Frontend)

**Validation Approach:**
- All testing performed through frontend UI
- Every task includes Manual Test Step and User Test Prompt
- After all tasks in sprint pass, commit and push to `main`
- If any test fails, fix and retest before pushing

**Test Execution:**
1. Start backend: `python -m uvicorn main:app --reload --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser to `http://localhost:3000`
4. Execute Manual Test Step for each task
5. Verify expected result matches actual result
6. If pass, mark task complete; if fail, debug and retry

**Example Test Flow:**
- Task: Implement user registration
- Manual Test Step: Fill registration form with email/password/phone → click "Create Account" → verify success message
- User Test Prompt: "Register a new account and confirm you see the phone verification screen."
- Expected Result: User redirected to OTP verification screen, success toast visible
- Actual Result: [Tester fills in after execution]

---

## 🔟 DYNAMIC SPRINT PLAN & BACKLOG

---

## 🧱 S0 – ENVIRONMENT SETUP & FRONTEND CONNECTION

**Objectives:**
- Create FastAPI skeleton with `/api/v1` base path and `/healthz` endpoint
- Connect to MongoDB Atlas using `MONGODB_URI`
- Enable CORS for frontend origin
- Replace dummy API URLs in frontend with real backend URLs
- Initialize Git repository at root, set default branch to `main`, push to GitHub
- Create single `.gitignore` file at root

**User Stories:**
- As a developer, I need a working FastAPI server so I can build API endpoints
- As a developer, I need MongoDB Atlas connection so I can store data
- As a frontend, I need CORS enabled so I can make API requests
- As a team, I need Git initialized so we can track changes

**Tasks:**

### Task 1: Create FastAPI project structure
- Create `main.py` with FastAPI app instance
- Create `app/` directory with `__init__.py`
- Create `app/api/` directory for route modules
- Create `app/models/` directory for Pydantic models
- Create `app/db/` directory for database connection
- Create `app/core/` directory for config and utilities
- Create `requirements.txt` with dependencies: `fastapi`, `uvicorn[standard]`, `motor`, `pydantic`, `pydantic-settings`, `python-jose[cryptography]`, `passlib[argon2]`, `python-multipart`, `twilio`, `httpx`
- **Manual Test Step:** Run `pip install -r requirements.txt` → verify no errors
- **User Test Prompt:** "Install dependencies and confirm all packages install successfully."

### Task 2: Implement `/healthz` endpoint with MongoDB ping
- Create `app/db/mongodb.py` with Motor async client connection
- Load `MONGODB_URI` from environment variables
- Implement `get_database()` function returning database instance
- Create `app/api/health.py` with `GET /healthz` endpoint
- Endpoint performs `db.command('ping')` and returns `{ "status": "healthy", "database": "connected", "timestamp": "..." }`
- Handle connection errors gracefully
- **Manual Test Step:** Start backend → open browser to `http://localhost:8000/healthz` → verify JSON response with "connected" status
- **User Test Prompt:** "Start the backend and navigate to /healthz. Confirm you see a healthy status with database connected."

### Task 3: Configure CORS for frontend
- Create `app/core/config.py` with Pydantic Settings class
- Load `CORS_ORIGINS` from environment (default: `http://localhost:3000`)
- Add CORS middleware to FastAPI app in `main.py`
- Allow credentials, all methods, all headers
- **Manual Test Step:** Start backend and frontend → open browser console → verify no CORS errors when frontend loads
- **User Test Prompt:** "Start both backend and frontend. Open browser console and confirm no CORS errors appear."

### Task 4: Mount API router at `/api/v1`
- Create `app/api/__init__.py` with APIRouter instance
- Include health router at `/api/v1`
- Mount router in `main.py`
- **Manual Test Step:** Navigate to `http://localhost:8000/api/v1/healthz` → verify same response as before
- **User Test Prompt:** "Access /api/v1/healthz and confirm the health check works at the new path."

### Task 5: Initialize Git and push to GitHub
- Run `git init` at project root
- Create `.gitignore` with entries: `__pycache__/`, `*.pyc`, `.env`, `.venv/`, `venv/`, `.DS_Store`, `*.log`
- Run `git add .` and `git commit -m "Initial commit: FastAPI skeleton with MongoDB connection"`
- Set default branch to `main`: `git branch -M main`
- Create GitHub repository (manual step)
- Add remote: `git remote add origin <repo-url>`
- Push: `git push -u origin main`
- **Manual Test Step:** Visit GitHub repository URL → verify code is visible
- **User Test Prompt:** "Check the GitHub repository and confirm the initial commit is present."

### Task 6: Update frontend API base URL
- Open `frontend/lib/auth.ts`
- Add constant: `const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'`
- Update all mock API calls to use real endpoints (will be implemented in later sprints)
- **Manual Test Step:** Start frontend → open Network tab → verify requests go to `http://localhost:8000/api/v1/*` (will 404 for now)
- **User Test Prompt:** "Open browser Network tab and confirm API requests target the backend URL."

**Definition of Done:**
- Backend runs on port 8000 without errors
- `/healthz` returns success with MongoDB connection status
- Frontend can make requests without CORS errors
- Git repository initialized and pushed to GitHub `main` branch
- `.gitignore` file created at root

**Post-Sprint:** Commit all changes and push to `main`

---

## 🧩 S1 – BASIC AUTH (SIGNUP / LOGIN / LOGOUT)

**Objectives:**
- Implement JWT-based signup, login, and logout
- Store users in MongoDB with Argon2 password hashing
- Send OTP via Twilio for phone verification
- Protect one backend route and one frontend page

**User Stories:**
- As a user, I can register with email/password/phone so I can create an account
- As a user, I can verify my phone with OTP so I can activate my account
- As a user, I can login with email/password so I can access my dashboard
- As a user, I can logout so I can end my session

**Tasks:**

### Task 1: Create User Pydantic model
- Create `app/models/user.py` with Pydantic v2 models
- Define `UserCreate` (email, password, phone)
- Define `UserInDB` (all fields including passwordHash, phoneVerified, etc.)
- Define `UserResponse` (safe fields for API responses)
- Add field validators for email format, password length (min 8), phone E.164 format
- **Manual Test Step:** Import models in Python shell → create instances → verify validation works
- **User Test Prompt:** "Test model validation by creating user instances with invalid data and confirming errors."

### Task 2: Implement password hashing utilities
- Create `app/core/security.py`
- Implement `hash_password(password: str) -> str` using Argon2
- Implement `verify_password(plain: str, hashed: str) -> bool`
- **Manual Test Step:** Hash a password → verify it → confirm returns True
- **User Test Prompt:** "Test password hashing by hashing 'test123' and verifying it matches."

### Task 3: Implement JWT token utilities
- Add to `app/core/security.py`
- Implement `create_access_token(data: dict) -> str` using python-jose
- Implement `decode_access_token(token: str) -> dict` with expiry validation
- Load `JWT_SECRET` and `JWT_EXPIRES_IN` from config
- **Manual Test Step:** Create token → decode it → verify payload matches
- **User Test Prompt:** "Generate a JWT token and decode it to confirm the payload is correct."

### Task 4: Implement OTP generation and Twilio SMS
- Create `app/core/otp.py`
- Implement `generate_otp() -> str` (6-digit random number)
- Create `app/integrations/twilio_client.py`
- Implement `send_sms(to: str, message: str) -> bool` using Twilio API
- Load Twilio credentials from config
- **Manual Test Step:** Call `send_sms("+15551234567", "Your OTP is 123456")` → verify SMS received (use your real phone)
- **User Test Prompt:** "Send a test SMS to your phone and confirm you receive it."

### Task 5: Implement `POST /api/v1/auth/signup`
- Create `app/api/auth.py` with signup endpoint
- Validate email uniqueness (query MongoDB)
- Hash password with Argon2
- Generate OTP and store in user document with 10-minute expiry
- Send OTP via Twilio
- Insert user into `users` collection
- Return user data (without password) and success message
- **Manual Test Step:** Open frontend → fill registration form → submit → verify success toast and redirect to OTP screen
- **User Test Prompt:** "Register a new account via the frontend and confirm you receive an OTP via SMS."

### Task 6: Implement `POST /api/v1/auth/verify-phone`
- Add verify-phone endpoint to `app/api/auth.py`
- Validate OTP matches stored value and hasn't expired
- Update user `phoneVerified` to true
- Clear OTP fields
- Generate JWT token
- Return token and user data
- **Manual Test Step:** Enter OTP from SMS → submit → verify success toast and redirect to dashboard
- **User Test Prompt:** "Enter the OTP you received and confirm you're redirected to the dashboard."

### Task 7: Implement `POST /api/v1/auth/login`
- Add login endpoint to `app/api/auth.py`
- Query user by email
- Verify password with Argon2
- Check phone is verified
- Generate JWT token
- Return token and user data
- **Manual Test Step:** Navigate to login page → enter credentials → submit → verify redirect to dashboard
- **User Test Prompt:** "Log in with your registered account and confirm you reach the dashboard."

### Task 8: Implement `POST /api/v1/auth/logout`
- Add logout endpoint to `app/api/auth.py`
- Return success message (token invalidation handled client-side)
- **Manual Test Step:** Click logout button in frontend → verify redirect to landing page
- **User Test Prompt:** "Click the logout button and confirm you're redirected to the home page."

### Task 9: Implement `GET /api/v1/auth/me`
- Add me endpoint to `app/api/auth.py`
- Create JWT dependency for protected routes
- Extract user ID from token
- Query user from database
- Return user profile data
- **Manual Test Step:** Login → navigate to settings page → verify profile data loads
- **User Test Prompt:** "After logging in, go to Settings and confirm your profile information displays correctly."

### Task 10: Update frontend auth.ts to use real API
- Replace mock functions in `frontend/lib/auth.ts` with real API calls
- Use `fetch()` or `axios` to call backend endpoints
- Store JWT token in localStorage
- Include token in Authorization header for protected requests
- **Manual Test Step:** Complete full auth flow (register → verify → login → logout) → verify all steps work
- **User Test Prompt:** "Complete the entire authentication flow and confirm all steps work end-to-end."

**Definition of Done:**
- Users can register with email/password/phone
- OTP sent via Twilio and verified successfully
- Users can login and receive JWT token
- Protected routes require valid JWT
- Logout clears session

**Post-Sprint:** Commit all changes and push to `main`

---

## 🧩 S2 – PROPERTY DISCOVERY

**Objectives:**
- Implement Airbnb URL parsing and scraping
- Return unavailable properties matching search criteria
- Handle anti-bot measures with Bright Data proxies

**User Stories:**
- As a user, I can paste an Airbnb search URL so I can discover unavailable properties
- As a user, I can see property details (name, location, price, dates) so I can decide which to watch

**Tasks:**

### Task 1: Create Property Pydantic models
- Create `app/models/property.py`
- Define `PropertyDiscoveryRequest` (searchUrl)
- Define `PropertyResult` (id, name, location, price, imageUrl, dates, guests, status)
- Define `PropertyDiscoveryResponse` (properties list, count)
- **Manual Test Step:** Import models → create instances → verify validation
- **User Test Prompt:** "Test property models with sample data."

### Task 2: Implement Airbnb URL parser
- Create `app/services/airbnb_parser.py`
- Implement `parse_search_url(url: str) -> dict` to extract location, dates, guests, filters
- Handle various Airbnb URL formats
- **Manual Test Step:** Parse sample URL → verify extracted parameters are correct
- **User Test Prompt:** "Test URL parsing with a real Airbnb search URL."

### Task 3: Implement Bright Data scraping client
- Create `app/integrations/brightdata_client.py`
- Implement `scrape_airbnb_properties(search_params: dict) -> list` using Bright Data proxy
- Rotate proxies and user-agents
- Parse Airbnb API response
- Filter for unavailable properties only
- Limit to 20 results
- **Manual Test Step:** Call scraper with test parameters → verify properties returned
- **User Test Prompt:** "Test the scraper and confirm it returns unavailable properties."

### Task 4: Implement `POST /api/v1/properties/discover`
- Create `app/api/properties.py` with discover endpoint
- Validate Airbnb URL format
- Parse URL to extract search criteria
- Call Bright Data scraper
- Return property results
- Handle errors (blocking, timeouts, invalid URLs)
- **Manual Test Step:** Open frontend discover page → paste Airbnb URL → submit → verify properties display
- **User Test Prompt:** "Paste an Airbnb search URL and confirm you see unavailable properties."

**Definition of Done:**
- Users can paste Airbnb search URLs
- Backend scrapes and returns unavailable properties
- Properties display in frontend with details
- Anti-bot measures working (>95% success rate)

**Post-Sprint:** Commit all changes and push to `main`

---

## 🧩 S3 – WATCHLIST MANAGEMENT

**Objectives:**
- Implement CRUD operations for watches
- Enforce 5-watch limit per user
- Support frequency tiers and status management

**User Stories:**
- As a user, I can add properties to my watchlist so I can monitor them
- As a user, I can view all my watches so I can track what I'm monitoring
- As a user, I can edit watch settings so I can change frequency or pause scanning
- As a user, I can delete watches so I can stop monitoring properties

**Tasks:**

### Task 1: Create Watch Pydantic models
- Create `app/models/watch.py`
- Define `WatchCreate` (propertyId, propertyName, propertyUrl, location, checkInDate, checkOutDate, guests, price, frequency, partialMatch)
- Define `WatchUpdate` (frequency, status, partialMatch - all optional)
- Define `WatchResponse` (all fields for API responses)
- **Manual Test Step:** Import models → create instances → verify validation
- **User Test Prompt:** "Test watch models with sample data."

### Task 2: Implement `POST /api/v1/watches`
- Create `app/api/watches.py` with create endpoint
- Require JWT authentication
- Validate user has < 5 active watches
- Validate dates (checkIn >= today, checkOut > checkIn)
- Calculate `expiresAt` (checkInDate at 23:59:59)
- Calculate initial `nextScanAt` based on frequency
- Insert watch into `watches` collection
- Return watch data
- **Manual Test Step:** Select properties in discover page → click "Monitor Selected" → verify redirect to watchlist with new watches
- **User Test Prompt:** "Add properties to your watchlist and confirm they appear in the watchlist page."

### Task 3: Implement `GET /api/v1/watches`
- Add list endpoint to `app/api/watches.py`
- Require JWT authentication
- Query all watches for current user
- Sort by createdAt descending
- Return watches array
- **Manual Test Step:** Navigate to watchlist page → verify all watches display with correct details
- **User Test Prompt:** "Open your watchlist and confirm all your watches are visible."

### Task 4: Implement `GET /api/v1/watches/:id`
- Add get-by-id endpoint to `app/api/watches.py`
- Require JWT authentication
- Verify watch belongs to current user
- Query watch details
- Query recent scan logs for this watch (last 10)
- Return watch with scan history
- **Manual Test Step:** Click on a watch → verify details and scan history display (scan history will be empty until S4)
- **User Test Prompt:** "Click on a watch to view its details."

### Task 5: Implement `PATCH /api/v1/watches/:id`
- Add update endpoint to `app/api/watches.py`
- Require JWT authentication
- Verify watch belongs to current user
- Update allowed fields (frequency, status, partialMatch)
- Recalculate `nextScanAt` if frequency changed
- Return updated watch
- **Manual Test Step:** Change watch frequency in watchlist → verify update saves and displays new frequency
- **User Test Prompt:** "Change a watch's frequency and confirm the update is saved."

### Task 6: Implement `DELETE /api/v1/watches/:id`
- Add delete endpoint to `app/api/watches.py`
- Require JWT authentication
- Verify watch belongs to current user
- Delete watch from database
- Return success message
- **Manual Test Step:** Click delete button on a watch → confirm deletion → verify watch removed from list
- **User Test Prompt:** "Delete a watch and confirm it's removed from your watchlist."

### Task 7: Implement `GET /api/v1/stats/dashboard`
- Create `app/api/stats.py` with dashboard endpoint
- Require JWT authentication
- Count active watches for user
- Count scans today (from scan_logs)
- Count alerts sent (from notifications)
- Query recent activity (last 10 scan logs + notifications)
- Return stats object
- **Manual Test Step:** Navigate to dashboard → verify stats display (will show 0s until S4/S5)
- **User Test Prompt:** "Open the dashboard and confirm stats are visible."

**Definition of Done:**
- Users can create watches (max 5)
- Users can view all watches
- Users can update watch settings
- Users can delete watches
- Dashboard stats display correctly

**Post-Sprint:** Commit all changes and push to `main`

---

## 🧩 S4 – SCANNING ENGINE

**Objectives:**
- Implement scheduled scanning jobs
- Support frequency tiers (daily/hourly/sniper)
- Log scan results
- Auto-expire watches at check-in date

**User Stories:**
- As a user, I want my watches scanned automatically so I don't have to check manually
- As a user, I want different scan frequencies so I can choose speed vs cost
- As a system, I need to log scan results so users can see activity

**Tasks:**

### Task 1: Create ScanLog Pydantic model
- Create `app/models/scan_log.py`
- Define `ScanLogCreate` (watchId, status, result, proxyUsed, userAgent, responseTime, errorMessage)
- Define `ScanLogResponse` (all fields for API responses)
- **Manual Test Step:** Import models → create instances → verify validation
- **User Test Prompt:** "Test scan log models with sample data."

### Task 2: Implement property availability checker
- Create `app/services/availability_checker.py`
- Implement `check_availability(property_url: str, dates: dict) -> str` using Bright Data
- Return "available", "unavailable", or "partial"
- Handle errors and retries
- **Manual Test Step:** Call checker with test property → verify result returned
- **User Test Prompt:** "Test availability checker with a known property."

### Task 3: Implement verify-retry logic
- Add to `app/services/availability_checker.py`
- Implement `verify_availability(property_url: str, dates: dict) -> bool`
- Check availability, wait 30 seconds, check again
- Return true only if available both times
- **Manual Test Step:** Call verify function → confirm 30-second delay → verify result
- **User Test Prompt:** "Test verify-retry logic and confirm it waits 30 seconds."

### Task 4: Implement scan job processor
- Create `app/services/scan_processor.py`
- Implement `process_scan(watch: dict) -> None`
- Check property availability
- Create scan log entry
- If available, trigger verify-retry
- If verified, create notification (will be sent in S5)
- Update watch `lastScannedAt` and `nextScanAt`
- **Manual Test Step:** Manually trigger scan for a watch → verify scan log created
- **User Test Prompt:** "Trigger a manual scan and confirm a log entry is created."

### Task 5: Implement scheduled job runner
- Create `app/services/scheduler.py`
- Implement `run_scheduled_scans() -> None`
- Query watches where `nextScanAt <= now()` and status = "active"
- Process each watch
- Calculate next scan time based on frequency
- **Manual Test Step:** Run scheduler manually → verify watches scanned and nextScanAt updated
- **User Test Prompt:** "Run the scheduler and confirm watches are scanned."

### Task 6: Implement auto-expiry logic
- Add to `app/services/scheduler.py`
- Implement `expire_old_watches() -> None`
- Query watches where `expiresAt <= now()` and status != "expired"
- Update status to "expired"
- **Manual Test Step:** Create watch with past check-in date → run expiry → verify status changed to "expired"
- **User Test Prompt:** "Test watch expiry with a past date."

### Task 7: Add background task to FastAPI
- Update `main.py` to include startup event
- Start background thread running scheduler every minute
- **Manual Test Step:** Start backend → wait 1 minute → verify scans running automatically
- **User Test Prompt:** "Start the backend and confirm scans run automatically after 1 minute."

### Task 8: Update watchlist to show scan status
- Frontend already displays `lastScannedAt` from watch data
- Verify backend returns correct timestamps
- **Manual Test Step:** Open watchlist → verify "Last checked: X mins ago" displays correctly
- **User Test Prompt:** "Check your watchlist and confirm last scan times are accurate."

**Definition of Done:**
- Watches scanned automatically based on frequency
- Scan logs created for each scan
- Verify-retry logic prevents false positives
- Watches auto-expire at check-in date
- Dashboard stats show scan counts

**Post-Sprint:** Commit all changes and push to `main`

---

## 🧩 S5 – SMS NOTIFICATIONS

**Objectives:**
- Send SMS alerts when availability detected
- Include deep links to property pages
- Handle Twilio delivery status

**User Stories:**
- As a user, I want to receive SMS alerts so I know immediately when a property is available
- As a user, I want deep links in SMS so I can book quickly

**Tasks:**

### Task 1: Create Notification Pydantic model
- Create `app/models/notification.py`
- Define `NotificationCreate` (watchId, userId, phone, message, deepLink)
- Define `NotificationResponse` (all fields for API responses)
- **Manual Test Step:** Import models → create instances → verify validation
- **User Test Prompt:** "Test notification models with sample data."

### Task 2: Implement SMS message formatter
- Create `app/services/notification_formatter.py`
- Implement `format_sms_message(property_name: str, dates: str, deep_link: str) -> str`
- Keep message under 160 chars
- Include emoji, property name, dates, and link
- **Manual Test Step:** Format test message → verify length < 160 chars
- **User Test Prompt:** "Test message formatting and confirm it's under 160 characters."

### Task 3: Implement deep link generator
- Add to `app/services/notification_formatter.py`
- Implement `generate_deep_link(property_url: str, check_in: str, check_out: str) -> str`
- Append checkin/checkout query params to Airbnb URL
- **Manual Test Step:** Generate link → open in browser → verify dates pre-filled
- **User Test Prompt:** "Generate a deep link and confirm it opens with dates pre-filled."

### Task 4: Implement notification sender
- Create `app/services/notification_sender.py`
- Implement `send_notification(watch: dict, user: dict) -> bool`
- Check if notification already sent in last 24 hours (prevent duplicates)
- Format SMS message
- Generate deep link
- Send via Twilio
- Create notification record in database
- **Manual Test Step:** Manually trigger notification → verify SMS received with correct link
- **User Test Prompt:** "Trigger a test notification and confirm you receive the SMS."

### Task 5: Integrate notifications into scan processor
- Update `app/services/scan_processor.py`
- After verify-retry confirms availability, call notification sender
- **Manual Test Step:** Create watch for available property → wait for scan → verify SMS received
- **User Test Prompt:** "Set up a watch and confirm you receive an SMS when availability is detected."

### Task 6: Implement Twilio webhook handler
- Create `app/api/webhooks.py`
- Implement `POST /api/v1/webhooks/twilio` endpoint
- Parse Twilio delivery status
- Update notification `deliveryStatus` in database
- **Manual Test Step:** Send SMS → check database → verify deliveryStatus updated
- **User Test Prompt:** "Send a notification and confirm the delivery status is tracked."

### Task 7: Test end-to-end notification flow
- Create watch for property
- Wait for scan to detect availability
- Verify SMS received within 60 seconds
- Click deep link and verify Airbnb opens with dates
- **Manual Test Step:** Complete full flow → verify all steps work
- **User Test Prompt:** "Complete the entire notification flow and confirm it works end-to-end."

**Definition of Done:**
- SMS notifications sent when availability detected
- Deep links work and pre-fill dates
- Delivery status tracked
- No duplicate notifications sent
- Full workflow functional: register → discover → watch → receive alert

**Post-Sprint:** Commit all changes and push to `main`

---

## ✅ FINAL VALIDATION

After completing all sprints, perform final end-to-end testing:

1. **Registration Flow:** Register new user → verify phone → login
2. **Discovery Flow:** Paste Airbnb URL → view properties → select up to 5
3. **Watchlist Flow:** Add watches → view list → edit frequency → pause/resume → delete
4. **Scanning Flow:** Wait for automatic scan → verify scan logs → check dashboard stats
5. **Notification Flow:** Detect availability → receive SMS → click deep link → verify Airbnb opens
6. **Settings Flow:** Update profile → change notification preferences → save

**Success Criteria Met:**
- ✅ All frontend features functional
- ✅ All manual tests pass
- ✅ Code pushed to `main` after each sprint
- ✅ Scanning engine >95% success rate
- ✅ SMS delivered within 60 seconds

---

## 🎯 WORKFLOW COMPLETION

After generating and saving this Backend-dev-plan.md file, switch to orchestrator mode to execute the development plan using:
- mode_slug: "orchestrator"
- reason: "Backend development plan is ready for execution"