#!/usr/bin/env python3
"""
Quick test script to verify BrightData configuration
"""
import asyncio
from app.core.config import settings
from app.integrations.brightdata_client import BrightDataClient
from app.services.airbnb_parser import ParsedAirbnbData

async def test_brightdata():
    print("=" * 60)
    print("BrightData Configuration Test")
    print("=" * 60)
    
    # Check settings
    print(f"\n1. Configuration from .env:")
    print(f"   API Key: {settings.BRIGHTDATA_API_KEY[:20]}..." if settings.BRIGHTDATA_API_KEY else "   API Key: NOT SET")
    print(f"   Dataset ID: {settings.BRIGHTDATA_DATASET_ID}")
    print(f"   API URL: {settings.BRIGHTDATA_API_URL}")
    
    # Initialize client
    print(f"\n2. Initializing BrightData Client...")
    client = BrightDataClient()
    
    # Check mode
    print(f"   Mock Mode: {client.mock_mode}")
    print(f"   API Key Present: {bool(client.api_key)}")
    
    if client.mock_mode:
        print("\n   ⚠️  WARNING: Client is in MOCK MODE")
        print("   This means it will generate fake data instead of real scraping")
    else:
        print("\n   ✅ SUCCESS: Client is configured for REAL scraping")
        print("   It will use Bright Data API for actual property data")
    
    # Test with a simple search
    print(f"\n3. Testing property scraping...")
    parsed_data = ParsedAirbnbData(
        location="San Francisco, CA",
        check_in="2025-01-15",
        check_out="2025-01-20",
        adults=2,
        children=0,
        infants=0,
        pets=0,
        raw_url="https://www.airbnb.com/s/San-Francisco--CA/homes"
    )
    
    try:
        properties = await client.scrape_properties(parsed_data, max_results=3)
        print(f"   Found {len(properties)} properties")
        
        if properties:
            print(f"\n4. Sample property:")
            prop = properties[0]
            print(f"   Name: {prop.get('propertyName')}")
            print(f"   Location: {prop.get('location')}")
            print(f"   Price: {prop.get('price')}")
            print(f"   URL: {prop.get('propertyUrl')}")
    
    except Exception as e:
        print(f"   ❌ Error during scraping: {str(e)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_brightdata())