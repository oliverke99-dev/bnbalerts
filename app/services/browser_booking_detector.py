"""
Browser-Based Booking Detection Service

This service identifies booked Airbnb properties using direct browser scraping
instead of external services like BrightData.
"""

import asyncio
from typing import List, Dict, Any, Set, Tuple
from datetime import date
import logging

from app.integrations.browser_scraper import BrowserScraper

logger = logging.getLogger(__name__)


class BrowserBookingDetector:
    """
    Service to detect booked properties using browser-based scraping.
    
    Strategy:
    1. Scrape properties for a location WITHOUT dates (shows all properties)
    2. Scrape properties for the SAME location WITH specific dates (shows only available)
    3. Compare the two result sets to identify properties that disappeared (booked)
    """
    
    def __init__(self):
        """Initialize the browser booking detector."""
        self.scraper = None
    
    async def detect_booked_properties(
        self,
        location: str,
        check_in: date,
        check_out: date,
        adults: int = 2,
        children: int = 0,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """
        Detect booked properties by comparing searches with and without dates.
        
        Args:
            location: Search location (e.g., "Austin, TX")
            check_in: Check-in date
            check_out: Check-out date
            adults: Number of adults
            children: Number of children
            max_results: Maximum properties to fetch per search
            
        Returns:
            Dictionary containing:
                - booked_properties: List of properties that are booked
                - available_properties: List of properties that are available
                - total_properties: Total properties found (without dates)
                - booked_count: Number of booked properties
                - available_count: Number of available properties
                - search_metadata: Information about the search
        """
        logger.info(f"Starting browser-based booking detection for {location} ({check_in} to {check_out})")
        
        # Initialize browser scraper
        self.scraper = BrowserScraper()
        await self.scraper.start()
        
        try:
            # Step 1: Search WITHOUT dates to get all properties
            logger.info("Step 1: Fetching all properties (no dates)...")
            all_properties = await self.scraper.scrape_airbnb_search(
                location=location,
                check_in=None,  # No dates
                check_out=None,
                adults=adults,
                children=children,
                max_results=max_results
            )
            
            logger.info(f"Found {len(all_properties)} total properties without date filter")
            
            # Step 2: Search WITH dates to get only available properties
            logger.info("Step 2: Fetching available properties (with dates)...")
            available_properties = await self.scraper.scrape_airbnb_search(
                location=location,
                check_in=check_in,
                check_out=check_out,
                adults=adults,
                children=children,
                max_results=max_results
            )
            
            logger.info(f"Found {len(available_properties)} available properties for specified dates")
            
            # Step 3: Compare results to identify booked properties
            logger.info("Step 3: Comparing results to identify booked properties...")
            booked_properties, available_props = self._compare_results(
                all_properties=all_properties,
                available_properties=available_properties,
                check_in=check_in,
                check_out=check_out
            )
            
            logger.info(f"Identified {len(booked_properties)} booked properties")
            
            # Construct response
            result = {
                "booked_properties": booked_properties,
                "available_properties": available_props,
                "total_properties": len(all_properties),
                "booked_count": len(booked_properties),
                "available_count": len(available_props),
                "search_metadata": {
                    "location": location,
                    "check_in": check_in.isoformat(),
                    "check_out": check_out.isoformat(),
                    "guests": adults + children,
                    "adults": adults,
                    "children": children
                }
            }
            
            return result
            
        finally:
            # Always close the browser
            await self.scraper.close()
    
    def _compare_results(
        self,
        all_properties: List[Dict[str, Any]],
        available_properties: List[Dict[str, Any]],
        check_in: date,
        check_out: date
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Compare two property lists to identify booked properties.
        
        Args:
            all_properties: Properties from search without dates
            available_properties: Properties from search with dates
            check_in: Check-in date for metadata
            check_out: Check-out date for metadata
            
        Returns:
            Tuple of (booked_properties, available_properties_enriched)
        """
        # Create a set of available property IDs for fast lookup
        available_ids: Set[str] = {
            prop.get("propertyId") for prop in available_properties
            if prop.get("propertyId")
        }
        
        # Identify booked properties (in all_properties but not in available_properties)
        booked_properties = []
        for prop in all_properties:
            property_id = prop.get("propertyId")
            if property_id and property_id not in available_ids:
                # Mark as booked
                booked_prop = prop.copy()
                booked_prop["status"] = "booked"
                booked_prop["availability"] = "unavailable"
                booked_prop["checkInDate"] = check_in.isoformat()
                booked_prop["checkOutDate"] = check_out.isoformat()
                booked_properties.append(booked_prop)
        
        # Enrich available properties with status
        available_props_enriched = []
        for prop in available_properties:
            enriched_prop = prop.copy()
            enriched_prop["status"] = "available"
            enriched_prop["availability"] = "available"
            enriched_prop["checkInDate"] = check_in.isoformat()
            enriched_prop["checkOutDate"] = check_out.isoformat()
            available_props_enriched.append(enriched_prop)
        
        return booked_properties, available_props_enriched
    
    async def detect_booked_from_url(
        self,
        search_url: str,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """
        Detect booked properties from an Airbnb search URL.
        
        This is a convenience method that parses the URL and calls detect_booked_properties.
        
        Args:
            search_url: Airbnb search URL with dates
            max_results: Maximum properties to fetch per search
            
        Returns:
            Dictionary with booking detection results
        """
        from app.services.airbnb_parser import AirbnbURLParser
        
        # Parse the URL
        parser = AirbnbURLParser()
        parsed_data = parser.parse(search_url)
        
        # Validate we have required data
        if not parsed_data.location:
            raise ValueError("Location is required in the search URL")
        
        if not parsed_data.check_in or not parsed_data.check_out:
            raise ValueError("Check-in and check-out dates are required in the search URL")
        
        # Convert date strings to date objects
        check_in = date.fromisoformat(parsed_data.check_in)
        check_out = date.fromisoformat(parsed_data.check_out)
        
        # Detect booked properties
        return await self.detect_booked_properties(
            location=parsed_data.location,
            check_in=check_in,
            check_out=check_out,
            adults=parsed_data.adults or 2,
            children=parsed_data.children or 0,
            max_results=max_results
        )


# Convenience function for quick booking detection
async def detect_booked_properties_browser(
    location: str,
    check_in: date,
    check_out: date,
    adults: int = 2,
    children: int = 0,
    max_results: int = 50
) -> Dict[str, Any]:
    """
    Convenience function to detect booked properties using browser scraping.
    
    Args:
        location: Search location
        check_in: Check-in date
        check_out: Check-out date
        adults: Number of adults
        children: Number of children
        max_results: Maximum properties per search
        
    Returns:
        Dictionary with booking detection results
    """
    detector = BrowserBookingDetector()
    return await detector.detect_booked_properties(
        location=location,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        children=children,
        max_results=max_results
    )