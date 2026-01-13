"""
BrightData Scraping Client

This module provides integration with BrightData's scraping services
for extracting Airbnb property data.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging
import random
import httpx

from app.core.config import settings
from app.services.airbnb_parser import ParsedAirbnbData
from app.core.constants import (
    MOCK_API_DELAY_SECONDS,
    MOCK_MIN_PROPERTIES,
    MOCK_MAX_PROPERTIES,
    MAX_POLL_ATTEMPTS,
    POLL_INTERVAL_SECONDS
)

logger = logging.getLogger(__name__)


class BrightDataScrapingError(Exception):
    """Base exception for BrightData scraping errors"""
    pass


class BrightDataAPIError(BrightDataScrapingError):
    """Exception raised when BrightData API returns an error"""
    pass


class BrightDataTimeoutError(BrightDataScrapingError):
    """Exception raised when scraping operation times out"""
    pass


class BrightDataClient:
    """
    Client for interacting with BrightData's scraping services.
    
    This client handles scraping Airbnb property data based on search parameters.
    Currently implements a robust mock for development, structured to be easily
    swapped with real API calls.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        dataset_id: Optional[str] = None,
        api_url: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        """
        Initialize BrightData client.
        
        Args:
            api_key: BrightData API key (defaults to settings)
            dataset_id: Dataset ID for Airbnb scraping (defaults to settings)
            api_url: BrightData API base URL (defaults to settings)
            timeout: Request timeout in seconds (defaults to settings)
        """
        self.api_key = api_key or settings.BRIGHTDATA_API_KEY
        self.dataset_id = dataset_id or settings.BRIGHTDATA_DATASET_ID
        self.api_url = api_url or settings.BRIGHTDATA_API_URL
        self.timeout = timeout or settings.BRIGHTDATA_TIMEOUT
        
        # Check if we're in mock mode (no API key configured)
        self.mock_mode = not self.api_key or self.api_key == ""
        
        if self.mock_mode:
            logger.info("BrightData client initialized in MOCK MODE (no API key configured)")
        else:
            logger.info(f"BrightData client initialized with API key and dataset: {self.dataset_id}")
    
    async def scrape_properties(
        self,
        parsed_data: ParsedAirbnbData,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Scrape Airbnb properties based on search parameters.
        
        Args:
            parsed_data: Parsed Airbnb search parameters
            max_results: Maximum number of properties to return
            
        Returns:
            List of property dictionaries matching PropertyCreate schema
            
        Raises:
            BrightDataAPIError: If API request fails
            BrightDataTimeoutError: If scraping times out
            BrightDataScrapingError: For other scraping errors
        """
        if self.mock_mode:
            logger.warning("⚠️  USING MOCK MODE - Generating fake property data")
            return await self._mock_scrape_properties(parsed_data, max_results)
        else:
            logger.info("✅ USING REAL MODE - Attempting BrightData API scraping")
            try:
                return await self._real_scrape_properties(parsed_data, max_results)
            except BrightDataScrapingError as e:
                logger.error(f"❌ BrightData API failed: {str(e)}")
                logger.warning("⚠️  Falling back to MOCK MODE due to API error")
                return await self._mock_scrape_properties(parsed_data, max_results)
    
    async def _mock_scrape_properties(
        self,
        parsed_data: ParsedAirbnbData,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Mock implementation of property scraping for development.
        
        Returns realistic property data that matches the PropertyCreate schema.
        """
        logger.info(f"[MOCK] Scraping properties for location: {parsed_data.location}")
        logger.info(f"[MOCK] Check-in: {parsed_data.check_in}, Check-out: {parsed_data.check_out}")
        logger.info(f"[MOCK] Guests: {parsed_data.adults + parsed_data.children}")
        
        # Simulate API delay
        await asyncio.sleep(MOCK_API_DELAY_SECONDS)
        
        # Generate mock properties
        properties = []
        num_properties = min(max_results, random.randint(MOCK_MIN_PROPERTIES, MOCK_MAX_PROPERTIES))
        
        # Mock property templates
        property_types = [
            "Cozy Studio Apartment",
            "Modern Loft",
            "Spacious 2BR Apartment",
            "Charming Cottage",
            "Luxury Penthouse",
            "Beach House",
            "Mountain Cabin",
            "Downtown Condo",
            "Historic Townhouse",
            "Garden Villa"
        ]
        
        amenities = [
            "with City Views",
            "near Downtown",
            "with Pool",
            "with Parking",
            "Pet Friendly",
            "with Balcony",
            "with Kitchen",
            "with Workspace",
            "with Garden",
            "Waterfront"
        ]
        
        # Use location from parsed data or default
        location = parsed_data.location or "Unknown Location"
        
        # Parse dates or use defaults
        try:
            check_in = date.fromisoformat(parsed_data.check_in) if parsed_data.check_in else date.today()
            check_out = date.fromisoformat(parsed_data.check_out) if parsed_data.check_out else date.today()
        except (ValueError, TypeError):
            check_in = date.today()
            check_out = date.today()
        
        # Calculate total guests
        total_guests = parsed_data.adults + parsed_data.children
        if total_guests == 0:
            total_guests = 2  # Default to 2 guests
        
        for i in range(num_properties):
            property_type = random.choice(property_types)
            amenity = random.choice(amenities)
            
            # Generate realistic property ID
            property_id = f"{random.randint(10000000, 99999999)}"
            
            # Generate price based on property type and guests
            base_price = random.randint(80, 400)
            if "Luxury" in property_type or "Penthouse" in property_type:
                base_price = random.randint(300, 800)
            elif "Studio" in property_type:
                base_price = random.randint(60, 150)
            
            # Adjust price for number of guests
            price_per_guest = base_price + (total_guests - 2) * 20
            price = max(price_per_guest, base_price)
            
            # Generate property data
            property_data = {
                "propertyId": property_id,
                "propertyName": f"{property_type} {amenity}",
                "propertyUrl": f"https://www.airbnb.com/rooms/{property_id}",
                "location": location,
                "price": f"${price}",
                "imageUrl": f"https://placehold.co/600x400/1e293b/94a3b8?text={property_type.replace(' ', '+')}",
                "guests": total_guests,
                "checkInDate": check_in.isoformat(),
                "checkOutDate": check_out.isoformat(),
            }
            
            properties.append(property_data)
        
        logger.info(f"[MOCK] Successfully scraped {len(properties)} properties")
        return properties
    
    async def _real_scrape_properties(
        self,
        parsed_data: ParsedAirbnbData,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Real implementation of property scraping using BrightData API.
        
        Uses BrightData's Dataset API to trigger and collect Airbnb property data.
        """
        logger.info(f"Initiating BrightData scrape for location: {parsed_data.location}")
        
        try:
            # Construct the trigger URL for BrightData's dataset API
            trigger_url = f"{self.api_url}/trigger"
            
            # Build search parameters for Airbnb
            # BrightData expects specific parameter format for Airbnb searches
            search_params = []
            
            # Add location
            if parsed_data.location:
                search_params.append({
                    "url": f"https://www.airbnb.com/s/{parsed_data.location}/homes",
                    "location": parsed_data.location
                })
            
            # Construct query parameters
            query_params = {}
            if parsed_data.check_in:
                query_params["checkin"] = parsed_data.check_in
            if parsed_data.check_out:
                query_params["checkout"] = parsed_data.check_out
            if parsed_data.adults:
                query_params["adults"] = str(parsed_data.adults)
            if parsed_data.children:
                query_params["children"] = str(parsed_data.children)
            
            # Add query params to search URL if any exist
            if query_params and search_params:
                query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
                search_params[0]["url"] = f"{search_params[0]['url']}?{query_string}"
            
            # Prepare the API request payload
            payload = [
                {
                    "url": search_params[0]["url"] if search_params else "https://www.airbnb.com",
                    "limit": max_results
                }
            ]
            
            # Set up headers with authentication
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Triggering BrightData dataset collection: {self.dataset_id}")
            logger.debug(f"Request payload: {payload}")
            
            # Make the API request using httpx
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Trigger the dataset collection
                response = await client.post(
                    trigger_url,
                    json=payload,
                    headers=headers,
                    params={"dataset_id": self.dataset_id}
                )
                
                # Check for API errors
                if response.status_code != 200:
                    error_detail = response.text
                    logger.error(f"BrightData API error (status {response.status_code}): {error_detail}")
                    raise BrightDataAPIError(
                        f"BrightData API returned status {response.status_code}: {error_detail}"
                    )
                
                # Parse the response
                response_data = response.json()
                logger.info(f"BrightData collection triggered successfully")
                logger.debug(f"Response data: {response_data}")
                
                # BrightData returns a snapshot_id that we need to poll for results
                snapshot_id = response_data.get("snapshot_id")
                if not snapshot_id:
                    raise BrightDataAPIError("No snapshot_id returned from BrightData API")
                
                # Poll for results (BrightData processes asynchronously)
                logger.info(f"Polling for results with snapshot_id: {snapshot_id}")
                properties = await self._poll_for_results(client, snapshot_id, headers)
                
                logger.info(f"Successfully scraped {len(properties)} properties from BrightData")
                return properties
            
        except httpx.TimeoutException:
            logger.error(f"BrightData scraping timed out after {self.timeout}s")
            raise BrightDataTimeoutError(
                f"Scraping operation timed out after {self.timeout} seconds"
            )
        except BrightDataScrapingError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"BrightData scraping failed: {str(e)}", exc_info=True)
            raise BrightDataScrapingError(f"Failed to scrape properties: {str(e)}")
    
    async def _poll_for_results(
        self,
        client: httpx.AsyncClient,
        snapshot_id: str,
        headers: Dict[str, str],
        max_attempts: int = MAX_POLL_ATTEMPTS,
        poll_interval: int = POLL_INTERVAL_SECONDS
    ) -> List[Dict[str, Any]]:
        """
        Poll BrightData API for scraping results.
        
        Args:
            client: HTTP client instance
            snapshot_id: The snapshot ID to poll for
            headers: Request headers with authentication
            max_attempts: Maximum number of polling attempts
            poll_interval: Seconds to wait between polls
            
        Returns:
            List of scraped property data
            
        Raises:
            BrightDataTimeoutError: If polling exceeds max attempts
            BrightDataAPIError: If API returns an error
        """
        results_url = f"{self.api_url}/snapshot/{snapshot_id}"
        
        for attempt in range(max_attempts):
            try:
                response = await client.get(results_url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")
                    
                    if status == "ready":
                        # Results are ready, extract and transform them
                        logger.info(f"Results ready after {attempt + 1} attempts")
                        raw_results = data.get("data", [])
                        return self._transform_api_response(raw_results)
                    
                    elif status in ["running", "pending"]:
                        # Still processing, wait and retry
                        logger.debug(f"Snapshot status: {status}, attempt {attempt + 1}/{max_attempts}")
                        await asyncio.sleep(poll_interval)
                        continue
                    
                    elif status == "failed":
                        error_msg = data.get("error", "Unknown error")
                        raise BrightDataAPIError(f"BrightData scraping failed: {error_msg}")
                    
                    else:
                        logger.warning(f"Unknown snapshot status: {status}")
                        await asyncio.sleep(poll_interval)
                        continue
                
                elif response.status_code == 404:
                    # Snapshot not found yet, wait and retry
                    logger.debug(f"Snapshot not found yet, attempt {attempt + 1}/{max_attempts}")
                    await asyncio.sleep(poll_interval)
                    continue
                
                else:
                    raise BrightDataAPIError(
                        f"Polling failed with status {response.status_code}: {response.text}"
                    )
                    
            except httpx.TimeoutException:
                logger.warning(f"Polling attempt {attempt + 1} timed out")
                if attempt == max_attempts - 1:
                    raise BrightDataTimeoutError("Polling for results timed out")
                await asyncio.sleep(poll_interval)
                continue
        
        # Max attempts reached
        raise BrightDataTimeoutError(
            f"Results not ready after {max_attempts * poll_interval} seconds"
        )
    
    def _transform_api_response(self, api_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform BrightData API response to match PropertyCreate schema.
        
        BrightData returns Airbnb data in their specific format. This method
        transforms it to match our application's property schema.
        
        Args:
            api_data: Raw API response data (list of property objects)
            
        Returns:
            List of transformed property dictionaries matching PropertyCreate schema
        """
        properties = []
        
        for item in api_data:
            try:
                # Extract property ID from URL or use provided ID
                property_id = item.get("id") or item.get("listing_id")
                if not property_id and item.get("url"):
                    # Try to extract ID from URL like: /rooms/12345678
                    url_parts = item.get("url", "").split("/rooms/")
                    if len(url_parts) > 1:
                        property_id = url_parts[1].split("?")[0]
                
                # Get property name/title
                property_name = (
                    item.get("name") or
                    item.get("title") or
                    item.get("listing_name") or
                    "Airbnb Property"
                )
                
                # Get location
                location = (
                    item.get("location") or
                    item.get("city") or
                    item.get("neighborhood") or
                    "Unknown Location"
                )
                
                # Get price (handle various formats)
                price = item.get("price") or item.get("price_per_night")
                if isinstance(price, (int, float)):
                    price = f"${int(price)}"
                elif not price:
                    price = "Price not available"
                
                # Get image URL
                image_url = (
                    item.get("image_url") or
                    item.get("thumbnail") or
                    item.get("picture_url") or
                    item.get("images", [{}])[0].get("url") if item.get("images") else None
                )
                
                # Get guest capacity
                guests = (
                    item.get("guests") or
                    item.get("max_guests") or
                    item.get("accommodates") or
                    2  # Default to 2 guests
                )
                
                # Get dates (may not always be in response)
                check_in = item.get("check_in") or item.get("checkin_date")
                check_out = item.get("check_out") or item.get("checkout_date")
                
                # Construct property URL
                property_url = item.get("url")
                if not property_url and property_id:
                    property_url = f"https://www.airbnb.com/rooms/{property_id}"
                
                # Build the property data object
                property_data = {
                    "propertyId": str(property_id) if property_id else f"unknown_{len(properties)}",
                    "propertyName": property_name,
                    "propertyUrl": property_url or "https://www.airbnb.com",
                    "location": location,
                    "price": price,
                    "imageUrl": image_url,
                    "guests": int(guests) if isinstance(guests, (int, float, str)) else 2,
                    "checkInDate": check_in,
                    "checkOutDate": check_out,
                }
                
                properties.append(property_data)
                
            except Exception as e:
                logger.warning(f"Failed to transform property data: {str(e)}, item: {item}")
                continue
        
        return properties
    
    async def health_check(self) -> bool:
        """
        Check if BrightData service is accessible.
        
        Returns:
            True if service is healthy, False otherwise
        """
        if self.mock_mode:
            logger.info("[MOCK] BrightData health check: OK")
            return True
        
        try:
            # TODO: Implement actual health check endpoint call
            # For now, just check if credentials are configured
            return bool(self.api_key and self.dataset_id)
        except Exception as e:
            logger.error(f"BrightData health check failed: {str(e)}")
            return False


# Convenience function for quick scraping
async def scrape_airbnb_properties(
    parsed_data: ParsedAirbnbData,
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """
    Convenience function to scrape Airbnb properties.
    
    Args:
        parsed_data: Parsed Airbnb search parameters
        max_results: Maximum number of properties to return
        
    Returns:
        List of property dictionaries
        
    Raises:
        BrightDataScrapingError: If scraping fails
    """
    client = BrightDataClient()
    return await client.scrape_properties(parsed_data, max_results)