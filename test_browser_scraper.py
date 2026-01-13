#!/usr/bin/env python3
"""Test script for browser-based Airbnb scraping"""

import asyncio
from datetime import date
from app.services.airbnb_parser import AirbnbURLParser
from app.integrations.browser_scraper import BrowserScraper


async def test_discover():
    # Parse a test URL
    url = 'https://www.airbnb.com/s/Austin--TX/homes?checkin=2024-06-01&checkout=2024-06-07&adults=2'
    parser = AirbnbURLParser()
    parsed = parser.parse(url)
    
    print('Testing browser scraper...')
    print(f'Location: {parsed.location}')
    print(f'Check-in: {parsed.check_in}')
    print(f'Check-out: {parsed.check_out}')
    print()
    
    # Test browser scraper
    check_in = date.fromisoformat(parsed.check_in) if parsed.check_in else None
    check_out = date.fromisoformat(parsed.check_out) if parsed.check_out else None
    
    print('Launching browser and scraping Airbnb...')
    async with BrowserScraper() as scraper:
        properties = await scraper.scrape_airbnb_search(
            location=parsed.location,
            check_in=check_in,
            check_out=check_out,
            adults=parsed.adults or 2,
            children=parsed.children or 0,
            max_results=5
        )
    
    print(f'\nFound {len(properties)} properties:')
    for i, prop in enumerate(properties[:3], 1):
        print(f'{i}. {prop["propertyName"]} - {prop["price"]}')
        print(f'   Location: {prop["location"]}')
        print(f'   URL: {prop["propertyUrl"]}')
        print()
    
    return len(properties) > 0


if __name__ == '__main__':
    result = asyncio.run(test_discover())
    status = 'PASSED' if result else 'FAILED'
    print(f'\nTest {status}')