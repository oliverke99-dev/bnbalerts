"""
Booking Detection Service

This service identifies booked Airbnb properties by comparing search results
with and without specific dates. Properties that appear in the no-date search
but disappear when dates are specified are considered booked.
"""

import asyncio
from typing import List, Dict, Any, Set, Tuple
from datetime import date
import logging

from app.services.airbnb_parser import ParsedAirbnbData
from app.integrations.apify_client import ApifyClient

logger = logging.getLogger(__name__)


class BookingDetector:
    """
    Service to detect booked properties by comparing availability with and without dates.
    
    Strategy:
    1. Scrape properties for a location WITHOUT dates (shows all properties)
    2. Scrape properties for the SAME location WITH specific dates (shows only available)
    3. Compare the two result sets to identify properties that disappeared (booked)
    """
    
    def __init__(self, client: ApifyClient = None):
        """
        Initialize the booking detector.
        
        Args:
            client: ApifyClient instance for scraping (creates new if None)
        """
        self.client = client or ApifyClient()
    
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
        logger.info(f"Starting booking detection for {location} ({check_in} to {check_out})")
        
        # Step 1: Search WITHOUT dates to get all properties
        logger.info("Step 1: Fetching all properties (no dates)...")
        all_properties = await self._search_without_dates(
            location=location,
            adults=adults,
            children=children,
            max_results=max_results
        )
        
        logger.info(f"Found {len(all_properties)} total properties without date filter")
        
        # Step 2: Search WITH dates to get only available properties
        logger.info("Step 2: Fetching available properties (with dates)...")
        available_properties = await self._search_with_dates(
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
            available_properties=available_properties
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
    
    async def _search_without_dates(
        self,
        location: str,
        adults: int,
        children: int,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Search for properties without date constraints.
        
        This returns all properties in the location regardless of availability.
        """
        # Create ParsedAirbnbData without dates
        parsed_data = ParsedAirbnbData(
            location=location,
            check_in=None,  # No dates
            check_out=None,
            adults=adults,
            children=children,
            infants=0,
            pets=0,
            raw_url=f"https://www.airbnb.com/s/{location}/homes"
        )
        
        # Scrape properties
        properties = await self.client.scrape_properties(
            parsed_data=parsed_data,
            max_results=max_results
        )
        
        return properties
    
    async def _search_with_dates(
        self,
        location: str,
        check_in: date,
        check_out: date,
        adults: int,
        children: int,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Search for properties with specific date constraints.
        
        This returns only properties available for the specified dates.
        """
        # Create ParsedAirbnbData with dates
        parsed_data = ParsedAirbnbData(
            location=location,
            check_in=check_in.isoformat(),
            check_out=check_out.isoformat(),
            adults=adults,
            children=children,
            infants=0,
            pets=0,
            raw_url=f"https://www.airbnb.com/s/{location}/homes?checkin={check_in.isoformat()}&checkout={check_out.isoformat()}"
        )
        
        # Scrape properties
        properties = await self.client.scrape_properties(
            parsed_data=parsed_data,
            max_results=max_results
        )
        
        return properties
    
    def _compare_results(
        self,
        all_properties: List[Dict[str, Any]],
        available_properties: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Compare two property lists to identify booked properties.
        
        Args:
            all_properties: Properties from search without dates
            available_properties: Properties from search with dates
            
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
                booked_properties.append(booked_prop)
        
        # Enrich available properties with status
        available_props_enriched = []
        for prop in available_properties:
            enriched_prop = prop.copy()
            enriched_prop["status"] = "available"
            enriched_prop["availability"] = "available"
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
async def detect_booked_properties(
    location: str,
    check_in: date,
    check_out: date,
    adults: int = 2,
    children: int = 0,
    max_results: int = 50
) -> Dict[str, Any]:
    """
    Convenience function to detect booked properties.
    
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
    detector = BookingDetector()
    return await detector.detect_booked_properties(
        location=location,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        children=children,
        max_results=max_results
    )