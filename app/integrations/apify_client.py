"""
Apify Scraping Client

This module provides integration with Apify's scraping services
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


class ApifyScrapingError(Exception):
    """Base exception for Apify scraping errors"""
    pass


class ApifyAPIError(ApifyScrapingError):
    """Exception raised when Apify API returns an error"""
    pass


class ApifyTimeoutError(ApifyScrapingError):
    """Exception raised when scraping operation times out"""
    pass


class ApifyClient:
    """
    Client for interacting with Apify's scraping services.
    
    This client handles scraping Airbnb property data based on search parameters.
    Currently implements a robust mock for development, structured to be easily
    swapped with real API calls.
    """
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        actor_id: Optional[str] = None,
        api_url: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        """
        Initialize Apify client.
        
        Args:
            api_token: Apify API token (defaults to settings)
            actor_id: Actor ID for Airbnb scraping (defaults to settings)
            api_url: Apify API base URL (defaults to settings)
            timeout: Request timeout in seconds (defaults to settings)
        """
        self.api_token = api_token or settings.APIFY_API_TOKEN
        self.actor_id = actor_id or settings.APIFY_ACTOR_ID
        self.api_url = api_url or settings.APIFY_API_URL
        self.timeout = timeout or settings.APIFY_TIMEOUT
        
        # Check if we're in mock mode (no API token configured)
        self.mock_mode = not self.api_token or self.api_token == ""
        
        if self.mock_mode:
            logger.info("Apify client initialized in MOCK MODE (no API token configured)")
        else:
            logger.info(f"Apify client initialized with API token and actor: {self.actor_id}")
    
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
            ApifyAPIError: If API request fails
            ApifyTimeoutError: If scraping times out
            ApifyScrapingError: For other scraping errors
        """
        if self.mock_mode:
            logger.warning("⚠️  USING MOCK MODE - Generating fake property data")
            return await self._mock_scrape_properties(parsed_data, max_results)
        else:
            logger.info("✅ USING REAL MODE - Attempting Apify API scraping")
            try:
                return await self._real_scrape_properties(parsed_data, max_results)
            except ApifyScrapingError as e:
                logger.error(f"❌ Apify API failed: {str(e)}")
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
        Real implementation of property scraping using Apify API.
        
        Uses Apify's Actor API to trigger and collect Airbnb property data.
        """
        # Double-check we have valid credentials
        if not self.api_token or not self.actor_id:
            logger.warning("⚠️  Apify credentials not configured, cannot use real mode")
            raise ApifyAPIError("Apify API token or actor ID not configured")
        
        logger.info(f"Initiating Apify scrape for location: {parsed_data.location}")
        
        try:
            # Construct the actor run URL
            run_url = f"{self.api_url}/acts/{self.actor_id}/runs"
            
            # Build input for Apify Airbnb scraper
            # Apify expects specific input format for Airbnb searches
            actor_input = {
                "locationQuery": parsed_data.location or "",
                "maxListings": max_results,
                "currency": "USD",
                "proxyConfiguration": {
                    "useApifyProxy": True
                }
            }
            
            # Add date parameters if provided
            if parsed_data.check_in:
                actor_input["checkIn"] = parsed_data.check_in
            if parsed_data.check_out:
                actor_input["checkOut"] = parsed_data.check_out
            
            # Add guest parameters
            if parsed_data.adults:
                actor_input["adults"] = parsed_data.adults
            if parsed_data.children:
                actor_input["children"] = parsed_data.children
            
            # Set up headers with authentication
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Triggering Apify actor run: {self.actor_id}")
            logger.debug(f"Actor input: {actor_input}")
            
            # Make the API request using httpx
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Trigger the actor run
                response = await client.post(
                    run_url,
                    json=actor_input,
                    headers=headers
                )
                
                # Check for API errors
                if response.status_code not in [200, 201]:
                    error_detail = response.text
                    logger.error(f"Apify API error (status {response.status_code}): {error_detail}")
                    raise ApifyAPIError(
                        f"Apify API returned status {response.status_code}: {error_detail}"
                    )
                
                # Parse the response
                response_data = response.json()
                logger.info(f"Apify actor run triggered successfully")
                logger.debug(f"Response data: {response_data}")
                
                # Apify returns a run object with an ID that we need to poll for results
                run_id = response_data.get("data", {}).get("id")
                if not run_id:
                    raise ApifyAPIError("No run ID returned from Apify API")
                
                # Poll for results (Apify processes asynchronously)
                logger.info(f"Polling for results with run ID: {run_id}")
                properties = await self._poll_for_results(client, run_id, headers)
                
                logger.info(f"Successfully scraped {len(properties)} properties from Apify")
                return properties
            
        except httpx.TimeoutException:
            logger.error(f"Apify scraping timed out after {self.timeout}s")
            raise ApifyTimeoutError(
                f"Scraping operation timed out after {self.timeout} seconds"
            )
        except ApifyScrapingError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Apify scraping failed: {str(e)}", exc_info=True)
            raise ApifyScrapingError(f"Failed to scrape properties: {str(e)}")
    
    async def _poll_for_results(
        self,
        client: httpx.AsyncClient,
        run_id: str,
        headers: Dict[str, str],
        max_attempts: int = MAX_POLL_ATTEMPTS,
        poll_interval: int = POLL_INTERVAL_SECONDS
    ) -> List[Dict[str, Any]]:
        """
        Poll Apify API for scraping results.
        
        Args:
            client: HTTP client instance
            run_id: The run ID to poll for
            headers: Request headers with authentication
            max_attempts: Maximum number of polling attempts
            poll_interval: Seconds to wait between polls
            
        Returns:
            List of scraped property data
            
        Raises:
            ApifyTimeoutError: If polling exceeds max attempts
            ApifyAPIError: If API returns an error
        """
        run_url = f"{self.api_url}/actor-runs/{run_id}"
        
        for attempt in range(max_attempts):
            try:
                response = await client.get(run_url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("data", {}).get("status")
                    
                    if status == "SUCCEEDED":
                        # Results are ready, fetch the dataset
                        logger.info(f"Run succeeded after {attempt + 1} attempts")
                        default_dataset_id = data.get("data", {}).get("defaultDatasetId")
                        
                        if not default_dataset_id:
                            raise ApifyAPIError("No dataset ID returned from completed run")
                        
                        # Fetch the dataset items
                        return await self._fetch_dataset(client, default_dataset_id, headers)
                    
                    elif status in ["RUNNING", "READY"]:
                        # Still processing, wait and retry
                        logger.debug(f"Run status: {status}, attempt {attempt + 1}/{max_attempts}")
                        await asyncio.sleep(poll_interval)
                        continue
                    
                    elif status == "FAILED":
                        error_msg = data.get("data", {}).get("statusMessage", "Unknown error")
                        raise ApifyAPIError(f"Apify scraping failed: {error_msg}")
                    
                    elif status == "ABORTED":
                        raise ApifyAPIError("Apify run was aborted")
                    
                    elif status == "TIMED-OUT":
                        raise ApifyTimeoutError("Apify run timed out")
                    
                    else:
                        logger.warning(f"Unknown run status: {status}")
                        await asyncio.sleep(poll_interval)
                        continue
                
                else:
                    raise ApifyAPIError(
                        f"Polling failed with status {response.status_code}: {response.text}"
                    )
                    
            except httpx.TimeoutException:
                logger.warning(f"Polling attempt {attempt + 1} timed out")
                if attempt == max_attempts - 1:
                    raise ApifyTimeoutError("Polling for results timed out")
                await asyncio.sleep(poll_interval)
                continue
        
        # Max attempts reached
        raise ApifyTimeoutError(
            f"Results not ready after {max_attempts * poll_interval} seconds"
        )
    
    async def _fetch_dataset(
        self,
        client: httpx.AsyncClient,
        dataset_id: str,
        headers: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Fetch dataset items from Apify.
        
        Args:
            client: HTTP client instance
            dataset_id: Dataset ID to fetch
            headers: Request headers with authentication
            
        Returns:
            List of transformed property data
            
        Raises:
            ApifyAPIError: If dataset fetch fails
        """
        dataset_url = f"{self.api_url}/datasets/{dataset_id}/items"
        
        try:
            response = await client.get(dataset_url, headers=headers)
            
            if response.status_code != 200:
                raise ApifyAPIError(
                    f"Failed to fetch dataset (status {response.status_code}): {response.text}"
                )
            
            raw_results = response.json()
            return self._transform_api_response(raw_results)
            
        except Exception as e:
            logger.error(f"Failed to fetch dataset: {str(e)}")
            raise ApifyAPIError(f"Dataset fetch failed: {str(e)}")
    
    def _transform_api_response(self, api_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform Apify API response to match PropertyCreate schema.
        
        Apify returns Airbnb data in their specific format. This method
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
                property_id = item.get("id") or item.get("listingId")
                if not property_id and item.get("url"):
                    # Try to extract ID from URL like: /rooms/12345678
                    url_parts = item.get("url", "").split("/rooms/")
                    if len(url_parts) > 1:
                        property_id = url_parts[1].split("?")[0]
                
                # Get property name/title
                property_name = (
                    item.get("name") or
                    item.get("title") or
                    item.get("listingName") or
                    "Airbnb Property"
                )
                
                # Get location
                location = (
                    item.get("location") or
                    item.get("city") or
                    item.get("neighborhood") or
                    item.get("address", {}).get("city") if isinstance(item.get("address"), dict) else None or
                    "Unknown Location"
                )
                
                # Get price (handle various formats)
                price = item.get("price") or item.get("pricePerNight")
                if isinstance(price, (int, float)):
                    price = f"${int(price)}"
                elif isinstance(price, dict):
                    # Apify might return price as object with currency
                    price_value = price.get("amount") or price.get("value")
                    if price_value:
                        price = f"${int(price_value)}"
                    else:
                        price = "Price not available"
                elif not price:
                    price = "Price not available"
                
                # Get image URL
                image_url = (
                    item.get("imageUrl") or
                    item.get("thumbnail") or
                    item.get("pictureUrl") or
                    item.get("images", [{}])[0].get("url") if item.get("images") else None
                )
                
                # Get guest capacity
                guests = (
                    item.get("guests") or
                    item.get("maxGuests") or
                    item.get("accommodates") or
                    2  # Default to 2 guests
                )
                
                # Get dates (may not always be in response)
                check_in = item.get("checkIn") or item.get("checkinDate")
                check_out = item.get("checkOut") or item.get("checkoutDate")
                
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
        Check if Apify service is accessible.
        
        Returns:
            True if service is healthy, False otherwise
        """
        if self.mock_mode:
            logger.info("[MOCK] Apify health check: OK")
            return True
        
        try:
            # Check if credentials are configured
            return bool(self.api_token and self.actor_id)
        except Exception as e:
            logger.error(f"Apify health check failed: {str(e)}")
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
        ApifyScrapingError: If scraping fails
    """
    client = ApifyClient()
    return await client.scrape_properties(parsed_data, max_results)