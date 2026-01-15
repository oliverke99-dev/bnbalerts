"""
Property details fetcher service.

This service fetches property details from a specific Airbnb property URL
and checks availability for given dates.
"""
import re
import logging
from datetime import date
from typing import Optional, Dict, Any
from app.integrations.apify_client import ApifyClient
from app.models.property import PropertyDetailsFetchResponse

logger = logging.getLogger(__name__)


class PropertyFetcher:
    """Service for fetching property details from Airbnb URLs."""
    
    def __init__(self, apify_client: ApifyClient):
        """
        Initialize the property fetcher.
        
        Args:
            apify_client: Apify client for scraping
        """
        self.apify_client = apify_client
        logger.info("PropertyFetcher initialized")
    
    def extract_property_id(self, property_url: str) -> str:
        """
        Extract property ID from Airbnb URL.
        
        Args:
            property_url: Full Airbnb property URL
            
        Returns:
            Property ID string
            
        Raises:
            ValueError: If property ID cannot be extracted
        """
        # Match patterns like:
        # https://www.airbnb.com/rooms/12345678
        # https://airbnb.com/rooms/12345678?...
        # https://www.airbnb.com/rooms/12345678/...
        pattern = r'/rooms/(\d+)'
        match = re.search(pattern, property_url)
        
        if not match:
            raise ValueError(f"Could not extract property ID from URL: {property_url}")
        
        property_id = match.group(1)
        logger.info(f"Extracted property ID: {property_id} from URL: {property_url}")
        return property_id
    
    async def fetch_property_details(
        self,
        property_url: str,
        check_in: date,
        check_out: date
    ) -> PropertyDetailsFetchResponse:
        """
        Fetch property details and check availability.
        
        This method:
        1. Extracts property ID from URL
        2. Constructs property URL with dates
        3. Scrapes property page
        4. Extracts property details
        5. Determines availability status
        
        Args:
            property_url: Full Airbnb property URL
            check_in: Check-in date
            check_out: Check-out date
            
        Returns:
            PropertyDetailsFetchResponse with property details and availability
            
        Raises:
            ValueError: If property details cannot be fetched
        """
        try:
            # Extract property ID
            property_id = self.extract_property_id(property_url)
            
            # Construct URL with dates
            # Format: https://www.airbnb.com/rooms/12345678?check_in=2024-06-01&check_out=2024-06-07
            base_url = f"https://www.airbnb.com/rooms/{property_id}"
            url_with_dates = f"{base_url}?check_in={check_in.isoformat()}&check_out={check_out.isoformat()}"
            
            logger.info(f"Fetching property details from: {url_with_dates}")
            
            # Scrape property page
            # Note: In production, this would use Apify or browser scraping
            # For now, we'll use mock data for development
            property_data = await self._scrape_property_page(url_with_dates, property_id)
            
            # Determine availability
            is_available = self._check_availability(property_data)
            current_status = "available" if is_available else "booked"
            
            # Build response
            response = PropertyDetailsFetchResponse(
                propertyId=property_id,
                propertyName=property_data.get("name", f"Property {property_id}"),
                location=property_data.get("location", "Location not available"),
                price=property_data.get("price", "$0"),
                imageUrl=property_data.get("image_url"),
                currentStatus=current_status,
                isAvailable=is_available,
                propertyUrl=base_url,
                checkIn=check_in,
                checkOut=check_out
            )
            
            logger.info(f"Successfully fetched property {property_id}: {current_status}")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching property details: {str(e)}")
            raise ValueError(f"Failed to fetch property details: {str(e)}")
    
    async def _scrape_property_page(self, url: str, property_id: str) -> Dict[str, Any]:
        """
        Scrape property page for details using browser scraping with shorter timeout.
        Falls back to httpx HTML scraping if Playwright is not available.
        
        Args:
            url: Property URL with dates
            property_id: Property ID
            
        Returns:
            Dictionary with property data
        """
        try:
            # Try browser scraping with shorter timeout and domcontentloaded
            from app.integrations.browser_scraper import BrowserScraper
            
            logger.info(f"Scraping property page with browser: {url}")
            
            async with BrowserScraper() as scraper:
                # Navigate to property page with shorter timeout and less strict wait condition
                await scraper.page.goto(url, wait_until="domcontentloaded", timeout=15000)
                await scraper.page.wait_for_timeout(3000)  # Wait for dynamic content
                
                # Extract property details
                property_data = {}
                
                # Get property name - try multiple selectors
                try:
                    # Try h1 first
                    name_element = await scraper.page.query_selector('h1')
                    if name_element:
                        property_data['name'] = (await name_element.inner_text()).strip()
                    
                    # If no h1 or empty, try title attribute
                    if not property_data.get('name'):
                        title = await scraper.page.title()
                        if title and 'Airbnb' in title:
                            # Extract property name from title (usually before " - Airbnb")
                            property_data['name'] = title.split(' - ')[0].strip()
                    
                    # Fallback
                    if not property_data.get('name'):
                        property_data['name'] = f"Airbnb Property {property_id}"
                except Exception as e:
                    logger.warning(f"Could not extract property name: {e}")
                    property_data['name'] = f"Airbnb Property {property_id}"
                
                # Get location
                try:
                    # Try multiple location selectors
                    location_selectors = [
                        '[data-section-id="LOCATION_DEFAULT"]',
                        'button[aria-label*="location"]',
                        'div:has-text("Hosted in")',
                    ]
                    for selector in location_selectors:
                        location_element = await scraper.page.query_selector(selector)
                        if location_element:
                            location_text = await location_element.inner_text()
                            if location_text:
                                property_data['location'] = location_text.strip()
                                break
                    
                    if not property_data.get('location'):
                        property_data['location'] = "Location available on Airbnb"
                except Exception as e:
                    logger.warning(f"Could not extract location: {e}")
                    property_data['location'] = "Location available on Airbnb"
                
                # Get price
                try:
                    price_selectors = [
                        '[data-testid="price-item-value"]',
                        'span:has-text("$")',
                        'div._1jo4hgw'
                    ]
                    for selector in price_selectors:
                        price_element = await scraper.page.query_selector(selector)
                        if price_element:
                            price_text = await price_element.inner_text()
                            if '$' in price_text:
                                property_data['price'] = price_text.strip()
                                break
                    
                    if not property_data.get('price'):
                        property_data['price'] = "See Airbnb for pricing"
                except Exception as e:
                    logger.warning(f"Could not extract price: {e}")
                    property_data['price'] = "See Airbnb for pricing"
                
                # Get image - try to get the main property image
                try:
                    image_selectors = [
                        'img[data-original-uri]',
                        'picture img',
                        'img[src*="pictures"]'
                    ]
                    for selector in image_selectors:
                        image_element = await scraper.page.query_selector(selector)
                        if image_element:
                            img_src = await image_element.get_attribute('src')
                            if img_src and 'pictures' in img_src:
                                property_data['image_url'] = img_src
                                break
                except Exception as e:
                    logger.warning(f"Could not extract image: {e}")
                    property_data['image_url'] = None
                
                # Check availability - look for reserve/book button or unavailable message
                try:
                    # Check for unavailable message first
                    unavailable = await scraper.page.query_selector('text="This place isn\'t available"')
                    if unavailable:
                        property_data['available'] = False
                        property_data['reserve_button'] = False
                    else:
                        # Look for reserve button
                        reserve_button = await scraper.page.query_selector('button:has-text("Reserve"), button:has-text("Book"), button:has-text("Request to book")')
                        property_data['available'] = reserve_button is not None
                        property_data['reserve_button'] = reserve_button is not None
                except Exception as e:
                    logger.warning(f"Could not check availability: {e}")
                    property_data['available'] = False
                    property_data['reserve_button'] = False
                
                logger.info(f"Successfully scraped property {property_id}: {property_data.get('name')}, available={property_data.get('available')}")
                return property_data
                
        except ImportError:
            logger.warning("Browser scraper not available, trying httpx fallback")
        except Exception as e:
            logger.error(f"Browser scraping failed: {str(e)}, trying httpx fallback")
        
        # Fallback - try httpx to fetch HTML and extract basic info
        return await self._scrape_with_httpx(url, property_id)
    
    async def _scrape_with_httpx(self, url: str, property_id: str) -> Dict[str, Any]:
        """
        Fallback scraping using httpx to fetch HTML and extract metadata.
        
        Args:
            url: Property URL
            property_id: Property ID
            
        Returns:
            Dictionary with property data extracted from HTML
        """
        import httpx
        
        property_data = {
            "name": f"Airbnb Property {property_id}",
            "location": "View on Airbnb for details",
            "price": "See Airbnb for pricing",
            "image_url": None,
            "available": False,
            "reserve_button": False
        }
        
        try:
            logger.info(f"Fetching property page with httpx: {url}")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
            
            async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    html = response.text
                    
                    # Extract title from <title> tag or og:title meta tag
                    # Pattern 1: <title>Property Name - Airbnb</title>
                    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
                    if title_match:
                        title = title_match.group(1).strip()
                        # Clean up title - remove " - Airbnb" suffix
                        if ' - Airbnb' in title:
                            title = title.split(' - Airbnb')[0].strip()
                        elif ' | Airbnb' in title:
                            title = title.split(' | Airbnb')[0].strip()
                        if title and title != "Airbnb":
                            property_data['name'] = title
                            logger.info(f"Extracted title from HTML: {title}")
                    
                    # Pattern 2: og:title meta tag
                    og_title_match = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
                    if not og_title_match:
                        og_title_match = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:title["\']', html, re.IGNORECASE)
                    if og_title_match and property_data['name'] == f"Airbnb Property {property_id}":
                        og_title = og_title_match.group(1).strip()
                        if og_title and og_title != "Airbnb":
                            property_data['name'] = og_title
                            logger.info(f"Extracted og:title from HTML: {og_title}")
                    
                    # Extract image from og:image meta tag
                    og_image_match = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
                    if not og_image_match:
                        og_image_match = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', html, re.IGNORECASE)
                    if og_image_match:
                        image_url = og_image_match.group(1).strip()
                        if image_url and 'muscache.com' in image_url:
                            property_data['image_url'] = image_url
                            logger.info(f"Extracted og:image from HTML: {image_url[:100]}...")
                    
                    # Extract location from og:description or page content
                    og_desc_match = re.search(r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']', html, re.IGNORECASE)
                    if not og_desc_match:
                        og_desc_match = re.search(r'<meta[^>]*content=["\']([^"\']+)["\'][^>]*property=["\']og:description["\']', html, re.IGNORECASE)
                    if og_desc_match:
                        description = og_desc_match.group(1).strip()
                        # Try to extract location from description
                        # Common patterns: "... in City, State" or "Located in City"
                        location_patterns = [
                            r'in\s+([A-Z][^.!?]+(?:,\s*[A-Z][^.!?]+)?)',
                            r'Located\s+in\s+([^.!?]+)',
                        ]
                        for pattern in location_patterns:
                            loc_match = re.search(pattern, description)
                            if loc_match:
                                location = loc_match.group(1).strip()
                                if len(location) > 3 and len(location) < 100:
                                    property_data['location'] = location
                                    logger.info(f"Extracted location from description: {location}")
                                    break
                    
                    logger.info(f"httpx scraping successful for property {property_id}: {property_data.get('name')}")
                else:
                    logger.warning(f"httpx request returned status {response.status_code}")
                    
        except Exception as e:
            logger.error(f"httpx scraping failed: {str(e)}")
        
        return property_data
    
    def _check_availability(self, property_data: Dict[str, Any]) -> bool:
        """
        Check if property is available based on scraped data.
        
        Looks for indicators like:
        - "Reserve" or "Book" button present
        - "Not available" or "Booked" messages absent
        - Price information present
        
        Args:
            property_data: Scraped property data
            
        Returns:
            True if available, False if booked
        """
        # Check for availability indicators
        has_reserve_button = property_data.get("reserve_button", False)
        is_marked_available = property_data.get("available", False)
        has_price = bool(property_data.get("price"))
        
        # Property is available if it has a reserve button and price
        is_available = has_reserve_button and is_marked_available and has_price
        
        logger.debug(f"Availability check: reserve_button={has_reserve_button}, "
                    f"available={is_marked_available}, has_price={has_price}, "
                    f"result={is_available}")
        
        return is_available
    
    async def validate_property_url(self, property_url: str) -> bool:
        """
        Validate that a property URL is valid and accessible.
        
        Args:
            property_url: Property URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Try to extract property ID
            property_id = self.extract_property_id(property_url)
            
            # In production, could also check if property exists
            # For now, just validate format
            return len(property_id) > 0
            
        except Exception as e:
            logger.warning(f"Invalid property URL: {property_url}, error: {str(e)}")
            return False