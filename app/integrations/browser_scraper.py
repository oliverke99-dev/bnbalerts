"""
Browser-Based Airbnb Scraper

This module provides direct browser-based scraping of Airbnb using Playwright/Puppeteer,
eliminating the need for external services like BrightData.
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


class BrowserScraper:
    """
    Direct browser-based scraper for Airbnb properties.
    
    Uses Playwright to automate a real browser and extract property data
    directly from Airbnb's website, mimicking a real user.
    """
    
    def __init__(self):
        """Initialize the browser scraper."""
        self.browser = None
        self.context = None
        self.page = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def start(self):
        """Start the browser instance."""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            
            # Launch browser with realistic settings
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )
            
            # Create context with realistic user agent and viewport
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set extra headers to appear more like a real browser
            await self.page.set_extra_http_headers({
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            })
            
            logger.info("Browser scraper started successfully")
            
        except ImportError:
            logger.error("Playwright not installed. Install with: pip install playwright && playwright install chromium")
            raise
        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}")
            raise
    
    async def close(self):
        """Close the browser instance."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
            logger.info("Browser scraper closed")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
    
    async def scrape_airbnb_search(
        self,
        location: str,
        check_in: Optional[date] = None,
        check_out: Optional[date] = None,
        adults: int = 2,
        children: int = 0,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Scrape Airbnb search results.
        
        Args:
            location: Search location (e.g., "Austin, TX")
            check_in: Check-in date (optional)
            check_out: Check-out date (optional)
            adults: Number of adults
            children: Number of children
            max_results: Maximum properties to return
            
        Returns:
            List of property dictionaries
        """
        if not self.page:
            await self.start()
        
        try:
            # Build search URL
            url = self._build_search_url(location, check_in, check_out, adults, children)
            
            logger.info(f"Navigating to: {url}")
            
            # Navigate to search page
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for listings to load
            await self.page.wait_for_selector('[data-testid="card-container"]', timeout=10000)
            
            # Random delay to appear more human-like
            await asyncio.sleep(1 + (hash(location) % 3))
            
            # Scroll to load more results
            await self._scroll_page()
            
            # Extract property data
            properties = await self._extract_properties(max_results)
            
            # Add search metadata
            for prop in properties:
                if check_in:
                    prop['checkInDate'] = check_in.isoformat()
                if check_out:
                    prop['checkOutDate'] = check_out.isoformat()
                prop['guests'] = adults + children
            
            logger.info(f"Successfully scraped {len(properties)} properties")
            
            return properties
            
        except Exception as e:
            logger.error(f"Error scraping Airbnb: {str(e)}")
            raise
    
    def _build_search_url(
        self,
        location: str,
        check_in: Optional[date],
        check_out: Optional[date],
        adults: int,
        children: int
    ) -> str:
        """Build Airbnb search URL with parameters."""
        # URL encode location
        location_encoded = location.replace(' ', '-').replace(',', '--')
        
        base_url = f"https://www.airbnb.com/s/{location_encoded}/homes"
        
        params = []
        
        if check_in:
            params.append(f"checkin={check_in.isoformat()}")
        if check_out:
            params.append(f"checkout={check_out.isoformat()}")
        if adults:
            params.append(f"adults={adults}")
        if children:
            params.append(f"children={children}")
        
        if params:
            return f"{base_url}?{'&'.join(params)}"
        
        return base_url
    
    async def _scroll_page(self):
        """Scroll page to load more results."""
        try:
            # Scroll down in increments
            for _ in range(3):
                await self.page.evaluate('window.scrollBy(0, window.innerHeight)')
                await asyncio.sleep(0.5)
            
            # Scroll back to top
            await self.page.evaluate('window.scrollTo(0, 0)')
            await asyncio.sleep(0.5)
            
        except Exception as e:
            logger.warning(f"Error scrolling page: {str(e)}")
    
    async def _extract_properties(self, max_results: int) -> List[Dict[str, Any]]:
        """
        Extract property data from the page.
        
        Args:
            max_results: Maximum number of properties to extract
            
        Returns:
            List of property dictionaries
        """
        properties = []
        
        try:
            # Get all listing cards
            cards = await self.page.query_selector_all('[data-testid="card-container"]')
            
            logger.info(f"Found {len(cards)} listing cards")
            
            for i, card in enumerate(cards[:max_results]):
                try:
                    property_data = await self._extract_property_from_card(card)
                    if property_data:
                        properties.append(property_data)
                except Exception as e:
                    logger.warning(f"Error extracting property {i}: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extracting properties: {str(e)}")
        
        return properties
    
    async def _extract_property_from_card(self, card) -> Optional[Dict[str, Any]]:
        """
        Extract property data from a single listing card.
        
        Args:
            card: Playwright element handle for the card
            
        Returns:
            Property dictionary or None if extraction fails
        """
        try:
            # Extract property URL and ID
            link = await card.query_selector('a[href*="/rooms/"]')
            if not link:
                return None
            
            href = await link.get_attribute('href')
            property_url = f"https://www.airbnb.com{href}" if href.startswith('/') else href
            
            # Extract property ID from URL
            property_id_match = re.search(r'/rooms/(\d+)', property_url)
            property_id = property_id_match.group(1) if property_id_match else f"unknown_{hash(property_url)}"
            
            # Extract property name/title
            title_elem = await card.query_selector('[data-testid="listing-card-title"]')
            property_name = await title_elem.inner_text() if title_elem else "Property"
            
            # Extract location
            subtitle_elem = await card.query_selector('[data-testid="listing-card-subtitle"]')
            location = await subtitle_elem.inner_text() if subtitle_elem else "Unknown Location"
            
            # Extract price
            price_elem = await card.query_selector('[data-testid="price-availability-row"]')
            if not price_elem:
                price_elem = await card.query_selector('span._1y74zjx')
            price = await price_elem.inner_text() if price_elem else "$0"
            
            # Clean up price (extract just the number)
            price_match = re.search(r'\$\d+', price)
            price = price_match.group(0) if price_match else price
            
            # Extract image URL
            img_elem = await card.query_selector('img')
            image_url = await img_elem.get_attribute('src') if img_elem else None
            
            # Extract rating (if available)
            rating_elem = await card.query_selector('[aria-label*="rating"]')
            rating = await rating_elem.inner_text() if rating_elem else None
            
            property_data = {
                'propertyId': property_id,
                'propertyName': property_name.strip(),
                'propertyUrl': property_url,
                'location': location.strip(),
                'price': price,
                'imageUrl': image_url,
                'guests': 2,  # Default, will be overridden by search params
                'rating': rating,
                'status': 'available'  # Will be determined by comparison logic
            }
            
            return property_data
            
        except Exception as e:
            logger.warning(f"Error extracting property from card: {str(e)}")
            return None


# Convenience function for quick scraping
async def scrape_airbnb(
    location: str,
    check_in: Optional[date] = None,
    check_out: Optional[date] = None,
    adults: int = 2,
    children: int = 0,
    max_results: int = 50
) -> List[Dict[str, Any]]:
    """
    Convenience function to scrape Airbnb properties.
    
    Args:
        location: Search location
        check_in: Check-in date (optional)
        check_out: Check-out date (optional)
        adults: Number of adults
        children: Number of children
        max_results: Maximum properties to return
        
    Returns:
        List of property dictionaries
    """
    async with BrowserScraper() as scraper:
        return await scraper.scrape_airbnb_search(
            location=location,
            check_in=check_in,
            check_out=check_out,
            adults=adults,
            children=children,
            max_results=max_results
        )