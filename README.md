# BnBAlerts Backend API

FastAPI backend for BnBAlerts cancellation monitoring and booking detection service.

## Prerequisites

- Python 3.13+
- MongoDB Atlas account
- pip or pip3

## Setup

1. **Install Xcode Command Line Tools** (macOS only):
   ```bash
   xcode-select --install
   ```

2. **Install Python dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Update the following required variables:
     - `MONGODB_URI`: Your MongoDB Atlas connection string
     - `JWT_SECRET`: A secure random string (min 32 characters)
   
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

4. **Run the development server**:
   ```bash
   python3 -m uvicorn main:app --reload --port 8000
   ```

5. **Access the API**:
   - API: http://localhost:8000
   - Health Check: http://localhost:8000/api/v1/healthz
   - Interactive Docs: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

## Project Structure

```
.
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── app/
│   ├── api/               # API route handlers
│   │   ├── health.py      # Health check endpoint
│   │   └── __init__.py    # API router configuration
│   ├── core/              # Core utilities
│   │   ├── config.py      # Settings and configuration
│   │   └── __init__.py
│   ├── db/                # Database connections
│   │   ├── mongodb.py     # MongoDB client setup
│   │   └── __init__.py
│   └── models/            # Pydantic models
│       └── __init__.py
```

## API Endpoints

### Health Check
- **GET** `/api/v1/healthz` - Check API and database health

### Booking Detection (New!)
- **POST** `/api/v1/properties/detect-bookings` - Detect booked properties from Airbnb URL
- **POST** `/api/v1/properties/detect-bookings-direct` - Detect booked properties with direct parameters

See [BOOKING_DETECTION_GUIDE.md](BOOKING_DETECTION_GUIDE.md) for detailed documentation.

## Development

### Sprint 0 Status ✅
- [x] FastAPI project structure created
- [x] MongoDB connection with health check
- [x] CORS configured for frontend
- [x] API router mounted at `/api/v1`
- [x] Git repository initialized
- [x] Frontend API base URL configured

### Next Steps
- Sprint 1: Authentication (signup, login, phone verification)
- Sprint 2: Property discovery (Airbnb scraping)
- Sprint 3: Watchlist management
- Sprint 4: Scanning engine
- Sprint 5: SMS notifications

## Testing

After starting the backend, test the health endpoint:

```bash
curl http://localhost:8000/api/v1/healthz
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Git Workflow

```bash
# Initialize repository (requires Xcode CLI tools)
git init
git add .
git commit -m "Initial commit: Sprint 0 - Environment setup"
git branch -M main

# Add remote and push
git remote add origin <your-repo-url>
git push -u origin main
```

## Environment Variables

See `.env.example` for all available configuration options.

Required for Sprint 0:
- `MONGODB_URI` - MongoDB Atlas connection string
- `JWT_SECRET` - Secret key for JWT tokens
- `CORS_ORIGINS` - Allowed frontend origins (default: http://localhost:3000)

## Troubleshooting

### Command not found: pip
Try using `pip3` instead:
```bash
pip3 install -r requirements.txt
```

### Xcode command line tools not installed
Install them with:
```bash
xcode-select --install
```

### MongoDB connection failed
- Verify your `MONGODB_URI` is correct
- Check that your IP is whitelisted in MongoDB Atlas
- Ensure your MongoDB user has proper permissions