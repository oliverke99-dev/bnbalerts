#!/usr/bin/env python3
"""
BrightData Configuration Verification Script

This script helps you verify your BrightData setup and diagnose issues.
Run this after configuring your .env file to ensure everything is working.
"""
import asyncio
import sys
from app.core.config import settings
from app.integrations.brightdata_client import BrightDataClient
from app.services.airbnb_parser import ParsedAirbnbData

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_section(number, text):
    """Print a formatted section header"""
    print(f"\n{number}. {text}")
    print("-" * 70)

def print_status(label, value, is_good=None):
    """Print a status line with optional color coding"""
    status = ""
    if is_good is True:
        status = "✅"
    elif is_good is False:
        status = "❌"
    else:
        status = "ℹ️"
    
    print(f"   {status} {label}: {value}")

async def verify_brightdata():
    """Main verification function"""
    print_header("BrightData Configuration Verification")
    
    # Step 1: Check Environment Variables
    print_section(1, "Checking Environment Variables")
    
    api_key = settings.BRIGHTDATA_API_KEY
    dataset_id = settings.BRIGHTDATA_DATASET_ID
    api_url = settings.BRIGHTDATA_API_URL
    timeout = settings.BRIGHTDATA_TIMEOUT
    
    # Check API Key
    if api_key and api_key != "":
        masked_key = api_key[:8] + "..." + api_key[-8:] if len(api_key) > 16 else api_key
        print_status("API Key", masked_key, True)
    else:
        print_status("API Key", "NOT SET", False)
        print("   ⚠️  WARNING: No API key configured - will use MOCK mode")
    
    # Check Dataset ID
    print_status("Dataset ID", dataset_id, bool(dataset_id))
    
    # Check API URL
    print_status("API URL", api_url, bool(api_url))
    
    # Check Timeout
    print_status("Timeout", f"{timeout} seconds", True)
    
    # Step 2: Initialize Client
    print_section(2, "Initializing BrightData Client")
    
    try:
        client = BrightDataClient()
        print_status("Client Created", "Success", True)
        
        # Check mode
        if client.mock_mode:
            print_status("Operating Mode", "MOCK MODE (using fake data)", False)
            print("\n   ⚠️  IMPORTANT: You are in MOCK MODE")
            print("   This means the system will generate fake property data.")
            print("   To use real BrightData scraping, you need to:")
            print("   1. Get a valid API key from BrightData dashboard")
            print("   2. Add it to your .env file as BRIGHTDATA_API_KEY")
            print("   3. Restart your backend server")
        else:
            print_status("Operating Mode", "REAL MODE (using BrightData API)", True)
            print("\n   ✅ SUCCESS: Client is configured for real scraping")
    except Exception as e:
        print_status("Client Creation", f"FAILED: {str(e)}", False)
        return
    
    # Step 3: Test Scraping
    print_section(3, "Testing Property Scraping")
    
    # Create test search parameters
    test_data = ParsedAirbnbData(
        location="San Francisco, CA",
        check_in="2025-02-01",
        check_out="2025-02-05",
        adults=2,
        children=0,
        infants=0,
        pets=0,
        raw_url="https://www.airbnb.com/s/San-Francisco--CA/homes"
    )
    
    print(f"   Testing with: {test_data.location}")
    print(f"   Dates: {test_data.check_in} to {test_data.check_out}")
    print(f"   Guests: {test_data.adults} adults")
    
    try:
        print("\n   Scraping properties (this may take a few seconds)...")
        properties = await client.scrape_properties(test_data, max_results=3)
        
        print_status("Scraping Result", f"Found {len(properties)} properties", True)
        
        if properties:
            print("\n   Sample Property:")
            prop = properties[0]
            print(f"      • Name: {prop.get('propertyName')}")
            print(f"      • Location: {prop.get('location')}")
            print(f"      • Price: {prop.get('price')}")
            print(f"      • Property ID: {prop.get('propertyId')}")
            print(f"      • URL: {prop.get('propertyUrl')}")
            
            # Check if it's mock data
            if "placehold.co" in str(prop.get('imageUrl', '')):
                print("\n   ⚠️  This appears to be MOCK DATA (placeholder images)")
            else:
                print("\n   ✅ This appears to be REAL DATA (actual Airbnb images)")
        
    except Exception as e:
        print_status("Scraping Test", f"FAILED: {str(e)}", False)
        print(f"\n   Error details: {type(e).__name__}")
        if hasattr(e, '__cause__') and e.__cause__:
            print(f"   Caused by: {str(e.__cause__)}")
    
    # Step 4: Summary and Recommendations
    print_section(4, "Summary and Recommendations")
    
    if client.mock_mode:
        print("\n   📋 CURRENT STATUS: Using Mock Data")
        print("\n   📝 TO GET REAL DATA:")
        print("   1. Log in to your BrightData account at https://brightdata.com")
        print("   2. Navigate to Settings → API Tokens")
        print("   3. Copy your API key")
        print("   4. Open your .env file and update:")
        print("      BRIGHTDATA_API_KEY=your_actual_api_key_here")
        print("   5. Verify your dataset ID (current: gd_l7q7dkf244hwjntr0)")
        print("   6. Restart your backend server")
        print("\n   📖 For detailed instructions, see: BRIGHTDATA_SETUP_GUIDE.md")
    else:
        print("\n   ✅ CURRENT STATUS: Configured for Real Data")
        print("\n   🎯 NEXT STEPS:")
        print("   1. Test in your application by searching for properties")
        print("   2. Monitor your BrightData usage in the dashboard")
        print("   3. Check for any API errors in your backend logs")
        print("\n   💡 TIP: Real scraping takes 5-30 seconds per search")
        print("   💰 REMINDER: BrightData charges per request - monitor your usage")
    
    print("\n" + "=" * 70)
    print()

def main():
    """Entry point"""
    try:
        asyncio.run(verify_brightdata())
    except KeyboardInterrupt:
        print("\n\nVerification cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()