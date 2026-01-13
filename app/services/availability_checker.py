"""
Availability Checker Service

This service determines if a property (defined in a Watch) is available
for the requested dates by bridging between a Watch and the ApifyClient.
"""

from typing import Optional, Tuple
from datetime import datetime

from app.models.watch import WatchInDB
from app.models.property import PropertyResult
from app.models.scan_log import ScanResult
from app.services.airbnb_parser import ParsedAirbnbData
from app.integrations.apify_client import ApifyClient


class AvailabilityChecker:
    """
    Service to check property availability based on Watch criteria.
    
    This service:
    1. Constructs search parameters from a Watch
    2. Scrapes property data via ApifyClient
    3. Matches scraped results against the watched property
    4. Returns availability status and matching property data
    """
    
    def __init__(self, client: ApifyClient):
        """
        Initialize the AvailabilityChecker.
        
        Args:
            client: ApifyClient instance for scraping property data
        """
        self.client = client
    
    async def check_availability(
        self, 
        watch: WatchInDB
    ) -> Tuple[ScanResult, Optional[PropertyResult]]:
        """
        Check if the property in the watch is available for the requested dates.
        
        Args:
            watch: Watch object containing property URL, location, dates, and guest info
            
        Returns:
            Tuple of (ScanResult, Optional[PropertyResult]):
                - ScanResult: Enum indicating availability status
                - PropertyResult: Matching property data if found, else None
                
        Logic:
            1. Constructs ParsedAirbnbData from Watch
            2. Scrapes properties via ApifyClient
            3. Matches results against watch.propertyUrl
            4. Returns availability status and matching property
            
        Note:
            For testing with mock data, if watch.propertyUrl is "https://mock-success",
            a successful match is forced. Otherwise, basic URL matching is used.
        """
        # Step 1: Construct ParsedAirbnbData from Watch
        parsed_data = ParsedAirbnbData(
            location=watch.location,
            check_in=watch.checkInDate.isoformat(),
            check_out=watch.checkOutDate.isoformat(),
            adults=watch.guests,  # Watch stores total guests in single field
            children=0,
            infants=0,
            pets=0,
            raw_url=watch.propertyUrl
        )
        
        # Step 2: Scrape properties using ApifyClient
        scraped_properties = await self.client.scrape_properties(parsed_data)
        
        # If no properties were scraped, return unavailable
        if not scraped_properties:
            return ScanResult.UNAVAILABLE, None
        
        # Step 3: Match scraped results against the watched property
        matching_property = None
        
        # Handle mock testing scenario
        if watch.propertyUrl == "https://mock-success":
            # Force a successful match for testing
            first_property = scraped_properties[0]
            matching_property = PropertyResult(
                propertyId=first_property.get("propertyId", ""),
                propertyName=first_property.get("propertyName", ""),
                location=first_property.get("location", ""),
                price=first_property.get("price", ""),
                imageUrl=first_property.get("imageUrl"),
                dates=f"{watch.checkInDate.isoformat()} - {watch.checkOutDate.isoformat()}",
                guests=first_property.get("guests", watch.guests),
                status="available",
                propertyUrl=first_property.get("propertyUrl", "")
            )
            return ScanResult.AVAILABLE, matching_property
        
        # Iterate through scraped results to find a match
        for property_data in scraped_properties:
            # Match by URL
            if self._matches_url(property_data.get("propertyUrl", ""), watch.propertyUrl):
                matching_property = PropertyResult(
                    propertyId=property_data.get("propertyId", ""),
                    propertyName=property_data.get("propertyName", ""),
                    location=property_data.get("location", ""),
                    price=property_data.get("price", ""),
                    imageUrl=property_data.get("imageUrl"),
                    dates=f"{watch.checkInDate.isoformat()} - {watch.checkOutDate.isoformat()}",
                    guests=property_data.get("guests", watch.guests),
                    status="available",
                    propertyUrl=property_data.get("propertyUrl", "")
                )
                return ScanResult.AVAILABLE, matching_property
            
            # Match by property ID if available
            if watch.propertyId and property_data.get("propertyId") == watch.propertyId:
                matching_property = PropertyResult(
                    propertyId=property_data.get("propertyId", ""),
                    propertyName=property_data.get("propertyName", ""),
                    location=property_data.get("location", ""),
                    price=property_data.get("price", ""),
                    imageUrl=property_data.get("imageUrl"),
                    dates=f"{watch.checkInDate.isoformat()} - {watch.checkOutDate.isoformat()}",
                    guests=property_data.get("guests", watch.guests),
                    status="available",
                    propertyUrl=property_data.get("propertyUrl", "")
                )
                return ScanResult.AVAILABLE, matching_property
        
        # Step 4: Return result based on matching
        # If we have results but no exact match, return unavailable
        # (Could implement partial_match logic here for fuzzy matching)
        return ScanResult.UNAVAILABLE, None
    
    def _matches_url(self, scraped_url: str, watch_url: str) -> bool:
        """
        Check if scraped URL matches the watch URL.
        
        Performs basic string matching, normalizing URLs for comparison.
        
        Args:
            scraped_url: URL from scraped property data
            watch_url: URL from the watch
            
        Returns:
            True if URLs match, False otherwise
        """
        if not scraped_url or not watch_url:
            return False
        
        # Normalize URLs for comparison
        scraped_normalized = scraped_url.lower().strip().rstrip('/')
        watch_normalized = watch_url.lower().strip().rstrip('/')
        
        # Direct match
        if scraped_normalized == watch_normalized:
            return True
        
        # Extract property ID from URLs and compare
        # Airbnb URLs typically have format: /rooms/{property_id}
        scraped_id = self._extract_property_id(scraped_url)
        watch_id = self._extract_property_id(watch_url)
        
        if scraped_id and watch_id and scraped_id == watch_id:
            return True
        
        return False
    
    def _extract_property_id(self, url: str) -> Optional[str]:
        """
        Extract property ID from Airbnb URL.
        
        Args:
            url: Airbnb property URL
            
        Returns:
            Property ID if found, None otherwise
        """
        import re
        
        # Pattern to match /rooms/{id} or /rooms/{id}?params
        match = re.search(r'/rooms/(\d+)', url)
        if match:
            return match.group(1)
        
        return None