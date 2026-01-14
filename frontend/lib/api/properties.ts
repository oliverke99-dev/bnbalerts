"use client";

// API Configuration
const API_BASE_URL = (globalThis as any).process?.env?.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Get token from localStorage
function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('bnb_alerts_token');
}

// Property interfaces matching backend models
export interface PropertyResult {
  id: string;
  name: string;
  location: string;
  price: string;
  imageUrl?: string;
  dates?: string;
  guests: number;
  status: string;
  url: string;
}

export interface PropertyDiscoveryResponse {
  properties: PropertyResult[];
  count: number;
}

export interface PropertyDiscoveryRequest {
  searchUrl: string;
  checkIn?: string;  // ISO date string (YYYY-MM-DD)
  checkOut?: string; // ISO date string (YYYY-MM-DD)
  guests?: number;
}

/**
 * Discover properties from an Airbnb search or property URL
 * Calls POST /api/v1/properties/discover
 *
 * @param request - The discovery request with URL and optional dates
 * @returns Promise with discovered properties
 * @throws Error if request fails or user is not authenticated
 */
export async function discoverProperties(request: PropertyDiscoveryRequest): Promise<PropertyDiscoveryResponse> {
  const token = getToken();
  
  if (!token) {
    throw new Error('Authentication required. Please log in.');
  }

  const response = await fetch(`${API_BASE_URL}/properties/discover`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to discover properties' }));
    throw new Error(error.detail || `Request failed with status ${response.status}`);
  }

  const data = await response.json();
  return data;
}

/**
 * Properties API client
 */
export const propertiesApi = {
  discover: discoverProperties,
};