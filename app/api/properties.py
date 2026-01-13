"""
Property Discovery API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
import logging

from app.models.property import (
    PropertyDiscoveryRequest,
    PropertyDiscoveryResponse,
    PropertyResult,
    PropertyDetailsFetchRequest,
    PropertyDetailsFetchResponse
)
from app.models.booking import (
    BookingDetectionRequest,
    BookingDetectionDirectRequest,
    BookingDetectionResponse,
    PropertyBookingStatus,
    SearchMetadata
)
from app.models.user import UserInDB
from app.api.auth import get_current_user
from app.services.airbnb_parser import AirbnbURLParser
from app.integrations.apify_client import ApifyClient
from app.services.booking_detector import BookingDetector
from app.services.property_fetcher import PropertyFetcher

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/discover", response_model=PropertyDiscoveryResponse)
async def discover_properties(
    request: PropertyDiscoveryRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> PropertyDiscoveryResponse:
    """
    Discover properties from an Airbnb URL.
    
    Handles two types of URLs:
    1. Specific property URLs (/rooms/123456) - Returns single property with availability
    2. Search URLs (/s/Location/homes) - Returns multiple properties from search
    
    Args:
        request: PropertyDiscoveryRequest containing the Airbnb URL
        current_user: Authenticated user from JWT token
        
    Returns:
        PropertyDiscoveryResponse with discovered properties
        
    Raises:
        HTTPException: 400 for invalid URL, 500 for scraping errors
    """
    try:
        # Check if this is a specific property URL (contains /rooms/)
        import re
        from datetime import date
        
        is_property_url = bool(re.search(r'/rooms/\d+', request.searchUrl))
        
        if is_property_url:
            # Handle specific property URL
            logger.info(f"User {current_user.email} fetching specific property from URL")
            
            # Use dates from request body first, then try to parse from URL
            check_in = request.checkIn
            check_out = request.checkOut
            
            # If dates not in request body, try to parse from URL
            if not check_in or not check_out:
                parser = AirbnbURLParser()
                try:
                    parsed_data = parser.parse(request.searchUrl)
                    check_in = date.fromisoformat(parsed_data.check_in) if parsed_data.check_in else check_in
                    check_out = date.fromisoformat(parsed_data.check_out) if parsed_data.check_out else check_out
                except:
                    # If parsing fails, dates might be in query params
                    from urllib.parse import urlparse, parse_qs
                    parsed_url = urlparse(request.searchUrl)
                    params = parse_qs(parsed_url.query)
                    check_in_str = params.get('check_in', [None])[0] or params.get('checkin', [None])[0]
                    check_out_str = params.get('check_out', [None])[0] or params.get('checkout', [None])[0]
                    if check_in_str and not check_in:
                        check_in = date.fromisoformat(check_in_str)
                    if check_out_str and not check_out:
                        check_out = date.fromisoformat(check_out_str)
            
            if not check_in or not check_out:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Check-in and check-out dates are required. Please provide dates either in the request or in the URL."
                )
            
            # Fetch property details
            apify_client = ApifyClient()
            fetcher = PropertyFetcher(apify_client)
            property_details = await fetcher.fetch_property_details(
                property_url=request.searchUrl,
                check_in=check_in,
                check_out=check_out
            )
            
            # Convert to PropertyResult
            property_result = PropertyResult(
                id=property_details.propertyId,
                name=property_details.propertyName,
                location=property_details.location,
                price=property_details.price,
                imageUrl=property_details.imageUrl,
                dates=f"{check_in.isoformat()} - {check_out.isoformat()}",
                guests=2,  # Default, could be extracted from URL if present
                status=property_details.currentStatus,
                url=property_details.propertyUrl
            )
            
            logger.info(f"Fetched specific property {property_details.propertyId}: {property_details.currentStatus}")
            
            return PropertyDiscoveryResponse(
                properties=[property_result],
                count=1
            )
        
        # Handle search URL (original behavior)
        # Parse the Airbnb URL
        parser = AirbnbURLParser()
        parsed_data = parser.parse(request.searchUrl)
        
        logger.info(f"User {current_user.email} discovering properties from search URL")
        
        # Try browser-based scraping first (real data, no API key needed)
        try:
            from app.integrations.browser_scraper import BrowserScraper
            from datetime import date
            
            logger.info("Using browser-based scraping for real Airbnb data")
            
            # Convert date strings to date objects if present
            check_in = date.fromisoformat(parsed_data.check_in) if parsed_data.check_in else None
            check_out = date.fromisoformat(parsed_data.check_out) if parsed_data.check_out else None
            
            # Use browser scraper
            async with BrowserScraper() as scraper:
                properties_data = await scraper.scrape_airbnb_search(
                    location=parsed_data.location or "Unknown",
                    check_in=check_in,
                    check_out=check_out,
                    adults=parsed_data.adults or 2,
                    children=parsed_data.children or 0,
                    max_results=20
                )
            
            logger.info(f"Browser scraping successful: {len(properties_data)} properties found")
            
        except ImportError:
            # Playwright not installed, fall back to Apify
            logger.warning("Playwright not installed, falling back to Apify")
            client = ApifyClient()
            properties_data = await client.scrape_properties(
                parsed_data=parsed_data,
                max_results=20
            )
        except Exception as browser_error:
            # Browser scraping failed, fall back to Apify
            logger.warning(f"Browser scraping failed: {str(browser_error)}, falling back to Apify")
            client = ApifyClient()
            properties_data = await client.scrape_properties(
                parsed_data=parsed_data,
                max_results=20
            )
        
        # Transform to PropertyResult objects
        properties = [
            PropertyResult(
                id=prop["propertyId"],
                name=prop["propertyName"],
                location=prop["location"],
                price=prop["price"],
                imageUrl=prop.get("imageUrl"),
                dates=f"{prop.get('checkInDate', '')} - {prop.get('checkOutDate', '')}",
                guests=prop["guests"],
                status=prop.get("status", "unavailable"),
                url=prop["propertyUrl"]
            )
            for prop in properties_data
        ]
        
        # Construct and return response
        return PropertyDiscoveryResponse(
            properties=properties,
            count=len(properties)
        )
        
    except ValueError as e:
        # Handle parsing errors from AirbnbURLParser
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Airbnb URL: {str(e)}"
        )
    except Exception as e:
        # Handle scraping or other unexpected errors
        logger.error(f"Property discovery failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to discover properties: {str(e)}"
        )


@router.post("/detect-bookings", response_model=BookingDetectionResponse)
async def detect_bookings_from_url(
    request: BookingDetectionRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> BookingDetectionResponse:
    """
    Detect booked properties by comparing searches with and without dates.
    
    This endpoint identifies properties that are booked for specific dates by:
    1. Searching for properties WITHOUT dates (shows all properties)
    2. Searching for properties WITH dates (shows only available)
    3. Comparing results to identify booked properties
    
    Args:
        request: BookingDetectionRequest containing Airbnb search URL with dates
        current_user: Authenticated user from JWT token
        
    Returns:
        BookingDetectionResponse with booked and available properties
        
    Raises:
        HTTPException: 400 for invalid URL, 500 for detection errors
    """
    try:
        logger.info(f"User {current_user.email} requested booking detection from URL")
        
        # Initialize booking detector
        detector = BookingDetector()
        
        # Detect booked properties from URL
        result = await detector.detect_booked_from_url(
            search_url=request.searchUrl,
            max_results=request.maxResults
        )
        
        # Transform raw result to response model
        booked_properties = [
            PropertyBookingStatus(**prop) for prop in result["booked_properties"]
        ]
        
        available_properties = [
            PropertyBookingStatus(**prop) for prop in result["available_properties"]
        ]
        
        search_metadata = SearchMetadata(**result["search_metadata"])
        
        response = BookingDetectionResponse(
            booked_properties=booked_properties,
            available_properties=available_properties,
            total_properties=result["total_properties"],
            booked_count=result["booked_count"],
            available_count=result["available_count"],
            search_metadata=search_metadata
        )
        
        logger.info(
            f"Booking detection complete: {result['booked_count']} booked, "
            f"{result['available_count']} available out of {result['total_properties']} total"
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Invalid request for booking detection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Booking detection failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect bookings: {str(e)}"
        )


@router.post("/detect-bookings-direct", response_model=BookingDetectionResponse)
async def detect_bookings_direct(
    request: BookingDetectionDirectRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> BookingDetectionResponse:
    """
    Detect booked properties using direct search parameters.
    
    This endpoint provides an alternative to URL-based detection by accepting
    search parameters directly (location, dates, guests).
    
    Args:
        request: BookingDetectionDirectRequest with search parameters
        current_user: Authenticated user from JWT token
        
    Returns:
        BookingDetectionResponse with booked and available properties
        
    Raises:
        HTTPException: 400 for invalid parameters, 500 for detection errors
    """
    try:
        logger.info(
            f"User {current_user.email} requested direct booking detection for "
            f"{request.location} ({request.checkIn} to {request.checkOut})"
        )
        
        # Initialize booking detector
        detector = BookingDetector()
        
        # Detect booked properties
        result = await detector.detect_booked_properties(
            location=request.location,
            check_in=request.checkIn,
            check_out=request.checkOut,
            adults=request.adults,
            children=request.children,
            max_results=request.maxResults
        )
        
        # Transform raw result to response model
        booked_properties = [
            PropertyBookingStatus(**prop) for prop in result["booked_properties"]
        ]
        
        available_properties = [
            PropertyBookingStatus(**prop) for prop in result["available_properties"]
        ]
        
        search_metadata = SearchMetadata(**result["search_metadata"])
        
        response = BookingDetectionResponse(
            booked_properties=booked_properties,
            available_properties=available_properties,
            total_properties=result["total_properties"],
            booked_count=result["booked_count"],
            available_count=result["available_count"],
            search_metadata=search_metadata
        )
        
        logger.info(
            f"Direct booking detection complete: {result['booked_count']} booked, "
            f"{result['available_count']} available out of {result['total_properties']} total"
        )
        
        return response
        
    except ValueError as e:
        logger.error(f"Invalid parameters for booking detection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameters: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Direct booking detection failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect bookings: {str(e)}"
        )


@router.post("/detect-bookings-browser", response_model=BookingDetectionResponse)
async def detect_bookings_browser(
    request: BookingDetectionDirectRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> BookingDetectionResponse:
    """
    Detect booked properties using direct browser scraping (no Apify required).
    
    This endpoint uses Playwright to scrape Airbnb directly, eliminating the need
    for external scraping services. It's slower but doesn't require API keys.
    
    Args:
        request: BookingDetectionDirectRequest with search parameters
        current_user: Authenticated user from JWT token
        
    Returns:
        BookingDetectionResponse with booked and available properties
        
    Raises:
        HTTPException: 400 for invalid parameters, 500 for detection errors
    """
    try:
        logger.info(
            f"User {current_user.email} requested browser-based booking detection for "
            f"{request.location} ({request.checkIn} to {request.checkOut})"
        )
        
        # Import browser detector
        from app.services.browser_booking_detector import BrowserBookingDetector
        
        # Initialize browser booking detector
        detector = BrowserBookingDetector()
        
        # Detect booked properties
        result = await detector.detect_booked_properties(
            location=request.location,
            check_in=request.checkIn,
            check_out=request.checkOut,
            adults=request.adults,
            children=request.children,
            max_results=request.maxResults
        )
        
        # Transform raw result to response model
        booked_properties = [
            PropertyBookingStatus(**prop) for prop in result["booked_properties"]
        ]
        
        available_properties = [
            PropertyBookingStatus(**prop) for prop in result["available_properties"]
        ]
        
        search_metadata = SearchMetadata(**result["search_metadata"])
        
        response = BookingDetectionResponse(
            booked_properties=booked_properties,
            available_properties=available_properties,
            total_properties=result["total_properties"],
            booked_count=result["booked_count"],
            available_count=result["available_count"],
            search_metadata=search_metadata
        )
        
        logger.info(
            f"Browser-based detection complete: {result['booked_count']} booked, "
            f"{result['available_count']} available out of {result['total_properties']} total"
        )
        
        return response
        
    except ImportError as e:
        logger.error(f"Playwright not installed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Browser scraping not available. Install playwright: pip install playwright && playwright install chromium"
        )
    except ValueError as e:
        logger.error(f"Invalid parameters for browser-based detection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameters: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Browser-based detection failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect bookings: {str(e)}"
        )


@router.post("/fetch-details", response_model=PropertyDetailsFetchResponse)
async def fetch_property_details(
    request: PropertyDetailsFetchRequest,
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> PropertyDetailsFetchResponse:
    """
    Fetch property details from a specific Airbnb property URL.
    
    This endpoint validates a property URL and fetches:
    - Property name, location, price, image
    - Current availability status for specified dates
    - Property ID extracted from URL
    
    This is used when users want to add a specific property to their watchlist.
    
    Args:
        request: PropertyDetailsFetchRequest with property URL and dates
        current_user: Authenticated user from JWT token
        
    Returns:
        PropertyDetailsFetchResponse with property details and availability
        
    Raises:
        HTTPException: 400 for invalid URL, 500 for fetch errors
    """
    try:
        logger.info(
            f"User {current_user.email} fetching property details from URL: {request.propertyUrl}"
        )
        
        # Initialize property fetcher with Apify client
        apify_client = ApifyClient()
        fetcher = PropertyFetcher(apify_client)
        
        # Fetch property details
        property_details = await fetcher.fetch_property_details(
            property_url=request.propertyUrl,
            check_in=request.checkIn,
            check_out=request.checkOut
        )
        
        logger.info(
            f"Successfully fetched property {property_details.propertyId}: "
            f"{property_details.currentStatus}"
        )
        
        return property_details
        
    except ValueError as e:
        logger.error(f"Invalid property URL or fetch failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid property URL or unable to fetch details: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Property details fetch failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch property details: {str(e)}"
        )