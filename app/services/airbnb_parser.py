"""
Airbnb URL Parser Service

This module provides functionality to parse Airbnb search URLs and extract
relevant search parameters such as location, dates, and guest counts.
"""

from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re


class ParsedAirbnbData(BaseModel):
    """Structured data model for parsed Airbnb search parameters."""
    
    location: Optional[str] = Field(None, description="Search location/query")
    check_in: Optional[str] = Field(None, description="Check-in date (YYYY-MM-DD)")
    check_out: Optional[str] = Field(None, description="Check-out date (YYYY-MM-DD)")
    adults: int = Field(0, description="Number of adults")
    children: int = Field(0, description="Number of children")
    infants: int = Field(0, description="Number of infants")
    pets: int = Field(0, description="Number of pets")
    currency: Optional[str] = Field(None, description="Currency code")
    raw_url: str = Field(..., description="Original URL")
    
    @field_validator('check_in', 'check_out')
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate date format is YYYY-MM-DD."""
        if v is None:
            return v
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError(f"Date must be in YYYY-MM-DD format, got: {v}")
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "location": "Paris--France",
                "check_in": "2024-06-01",
                "check_out": "2024-06-07",
                "adults": 2,
                "children": 0,
                "infants": 0,
                "pets": 0,
                "currency": "USD",
                "raw_url": "https://www.airbnb.com/s/Paris--France/homes"
            }
        }


class AirbnbURLParser:
    """
    Parser for Airbnb search URLs.
    
    Supports various Airbnb URL formats including:
    - /s/Location/homes
    - ?query=Location
    - International domains (airbnb.co.uk, airbnb.fr, etc.)
    """
    
    # Valid Airbnb domains
    VALID_DOMAINS = [
        'airbnb.com',
        'airbnb.co.uk',
        'airbnb.fr',
        'airbnb.de',
        'airbnb.es',
        'airbnb.it',
        'airbnb.ca',
        'airbnb.com.au',
        'airbnb.co.nz',
        'airbnb.ie',
        'airbnb.nl',
        'airbnb.be',
        'airbnb.ch',
        'airbnb.at',
        'airbnb.dk',
        'airbnb.se',
        'airbnb.no',
        'airbnb.fi',
        'airbnb.pt',
        'airbnb.pl',
        'airbnb.cz',
        'airbnb.gr',
        'airbnb.ru',
        'airbnb.com.br',
        'airbnb.com.mx',
        'airbnb.com.ar',
        'airbnb.cl',
        'airbnb.co',
        'airbnb.com.pe',
        'airbnb.co.cr',
        'airbnb.com.ec',
        'airbnb.co.in',
        'airbnb.co.id',
        'airbnb.com.my',
        'airbnb.com.sg',
        'airbnb.com.ph',
        'airbnb.co.th',
        'airbnb.co.kr',
        'airbnb.co.jp',
        'airbnb.com.hk',
        'airbnb.com.tw',
        'airbnb.cn',
        'airbnb.co.za',
        'airbnb.com.tr',
        'airbnb.ae',
    ]
    
    @classmethod
    def is_valid_airbnb_url(cls, url: str) -> bool:
        """
        Validate if the URL belongs to Airbnb.
        
        Args:
            url: The URL to validate
            
        Returns:
            True if valid Airbnb URL, False otherwise
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain in cls.VALID_DOMAINS
        except Exception:
            return False
    
    @classmethod
    def _extract_location_from_path(cls, path: str) -> Optional[str]:
        """
        Extract location from URL path.
        
        Handles formats like:
        - /s/Paris--France/homes
        - /s/New-York--NY--United-States/homes
        
        Args:
            path: URL path component
            
        Returns:
            Extracted location or None
        """
        # Pattern: /s/{location}/homes or /s/{location}
        match = re.search(r'/s/([^/]+)(?:/homes)?', path)
        if match:
            location = match.group(1)
            # URL decode and replace -- with comma-space for readability
            location = unquote(location)
            location = location.replace('--', ', ')
            location = location.replace('-', ' ')
            return location
        return None
    
    @classmethod
    def _parse_query_params(cls, query_params: Dict[str, list]) -> Dict[str, Any]:
        """
        Parse query parameters from URL.
        
        Args:
            query_params: Parsed query parameters dictionary
            
        Returns:
            Dictionary with extracted parameters
        """
        result = {}
        
        # Extract location from query parameter
        if 'query' in query_params:
            result['location'] = unquote(query_params['query'][0])
        elif 'location' in query_params:
            result['location'] = unquote(query_params['location'][0])
        
        # Extract dates
        if 'checkin' in query_params:
            result['check_in'] = query_params['checkin'][0]
        elif 'check_in' in query_params:
            result['check_in'] = query_params['check_in'][0]
        
        if 'checkout' in query_params:
            result['check_out'] = query_params['checkout'][0]
        elif 'check_out' in query_params:
            result['check_out'] = query_params['check_out'][0]
        
        # Extract guest counts
        if 'adults' in query_params:
            try:
                result['adults'] = int(query_params['adults'][0])
            except (ValueError, IndexError):
                result['adults'] = 0
        
        if 'children' in query_params:
            try:
                result['children'] = int(query_params['children'][0])
            except (ValueError, IndexError):
                result['children'] = 0
        
        if 'infants' in query_params:
            try:
                result['infants'] = int(query_params['infants'][0])
            except (ValueError, IndexError):
                result['infants'] = 0
        
        if 'pets' in query_params:
            try:
                result['pets'] = int(query_params['pets'][0])
            except (ValueError, IndexError):
                result['pets'] = 0
        
        # Extract currency
        if 'currency' in query_params:
            result['currency'] = query_params['currency'][0].upper()
        
        return result
    
    @classmethod
    def parse(cls, url: str) -> ParsedAirbnbData:
        """
        Parse an Airbnb URL and extract search parameters.
        
        Args:
            url: The Airbnb URL to parse
            
        Returns:
            ParsedAirbnbData object with extracted parameters
            
        Raises:
            ValueError: If URL is not a valid Airbnb URL
        """
        # Validate URL
        if not cls.is_valid_airbnb_url(url):
            raise ValueError(f"Invalid Airbnb URL: {url}")
        
        # Parse URL components
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Initialize result dictionary
        result = {
            'raw_url': url,
            'adults': 0,
            'children': 0,
            'infants': 0,
            'pets': 0,
        }
        
        # Extract location from path
        location_from_path = cls._extract_location_from_path(parsed.path)
        if location_from_path:
            result['location'] = location_from_path
        
        # Extract and merge query parameters
        query_data = cls._parse_query_params(query_params)
        result.update(query_data)
        
        # Create and return Pydantic model
        return ParsedAirbnbData(**result)
    
    @classmethod
    def parse_to_dict(cls, url: str) -> Dict[str, Any]:
        """
        Parse an Airbnb URL and return as dictionary.
        
        Args:
            url: The Airbnb URL to parse
            
        Returns:
            Dictionary with extracted parameters
            
        Raises:
            ValueError: If URL is not a valid Airbnb URL
        """
        parsed_data = cls.parse(url)
        return parsed_data.dict()


# Convenience function for quick parsing
def parse_airbnb_url(url: str) -> ParsedAirbnbData:
    """
    Convenience function to parse an Airbnb URL.
    
    Args:
        url: The Airbnb URL to parse
        
    Returns:
        ParsedAirbnbData object with extracted parameters
        
    Raises:
        ValueError: If URL is not a valid Airbnb URL
    """
    return AirbnbURLParser.parse(url)