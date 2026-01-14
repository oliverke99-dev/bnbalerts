"use client";

// API Configuration
const API_BASE_URL = (globalThis as any).process?.env?.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Get token from localStorage
function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('bnb_alerts_token');
}

// Watch interfaces matching backend models
export interface Watch {
  id: string;
  userId: string;
  propertyId: string;
  propertyName: string;
  propertyUrl: string;
  location: string;
  imageUrl?: string;
  checkInDate: string;
  checkOutDate: string;
  guests: number;
  price: string;
  frequency: 'daily' | 'hourly' | 'sniper';
  partialMatch: boolean;
  status: 'active' | 'paused' | 'expired';
  lastScannedAt?: string;
  nextScanAt?: string;
  expiresAt: string;
  createdAt: string;
  updatedAt: string;
}

export interface WatchCreate {
  propertyId: string;
  propertyName: string;
  propertyUrl: string;
  location: string;
  imageUrl?: string;
  checkInDate: string;
  checkOutDate: string;
  guests: number;
  price: string;
  frequency?: 'daily' | 'hourly' | 'sniper';
  partialMatch?: boolean;
}

export interface WatchUpdate {
  frequency?: 'daily' | 'hourly' | 'sniper';
  status?: 'active' | 'paused' | 'expired';
  partialMatch?: boolean;
}

/**
 * Get all watches for the current user
 * Calls GET /api/v1/watches
 * 
 * @returns Promise with list of watches
 * @throws Error if request fails or user is not authenticated
 */
export async function getWatches(): Promise<Watch[]> {
  const token = getToken();
  
  if (!token) {
    throw new Error('Authentication required. Please log in.');
  }

  const response = await fetch(`${API_BASE_URL}/watches`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to fetch watches' }));
    throw new Error(error.detail || `Request failed with status ${response.status}`);
  }

  const data = await response.json();
  return data;
}

/**
 * Get a specific watch by ID
 * Calls GET /api/v1/watches/{watch_id}
 * 
 * @param watchId - The watch ID
 * @returns Promise with watch details
 * @throws Error if request fails or user is not authenticated
 */
export async function getWatch(watchId: string): Promise<Watch> {
  const token = getToken();
  
  if (!token) {
    throw new Error('Authentication required. Please log in.');
  }

  const response = await fetch(`${API_BASE_URL}/watches/${watchId}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to fetch watch' }));
    throw new Error(error.detail || `Request failed with status ${response.status}`);
  }

  const data = await response.json();
  return data;
}

/**
 * Create a new watch
 * Calls POST /api/v1/watches
 * 
 * @param watchData - The watch creation data
 * @returns Promise with created watch
 * @throws Error if request fails or user is not authenticated
 */
export async function createWatch(watchData: WatchCreate): Promise<Watch> {
  const token = getToken();
  
  if (!token) {
    throw new Error('Authentication required. Please log in.');
  }

  const response = await fetch(`${API_BASE_URL}/watches`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(watchData),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to create watch' }));
    throw new Error(error.detail || `Request failed with status ${response.status}`);
  }

  const data = await response.json();
  return data;
}

/**
 * Update a watch
 * Calls PATCH /api/v1/watches/{watch_id}
 * 
 * @param watchId - The watch ID
 * @param updateData - The fields to update
 * @returns Promise with updated watch
 * @throws Error if request fails or user is not authenticated
 */
export async function updateWatch(watchId: string, updateData: WatchUpdate): Promise<Watch> {
  const token = getToken();
  
  if (!token) {
    throw new Error('Authentication required. Please log in.');
  }

  const response = await fetch(`${API_BASE_URL}/watches/${watchId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(updateData),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to update watch' }));
    throw new Error(error.detail || `Request failed with status ${response.status}`);
  }

  const data = await response.json();
  return data;
}

/**
 * Delete a watch
 * Calls DELETE /api/v1/watches/{watch_id}
 * 
 * @param watchId - The watch ID
 * @returns Promise with success message
 * @throws Error if request fails or user is not authenticated
 */
export async function deleteWatch(watchId: string): Promise<{ message: string }> {
  const token = getToken();
  
  if (!token) {
    throw new Error('Authentication required. Please log in.');
  }

  const response = await fetch(`${API_BASE_URL}/watches/${watchId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to delete watch' }));
    throw new Error(error.detail || `Request failed with status ${response.status}`);
  }

  const data = await response.json();
  return data;
}

/**
 * Watches API client
 */
export const watchesApi = {
  getAll: getWatches,
  getById: getWatch,
  create: createWatch,
  update: updateWatch,
  delete: deleteWatch,
};