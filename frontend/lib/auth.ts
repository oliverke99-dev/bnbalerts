"use client";

// API Configuration
// When NEXT_PUBLIC_API_URL is not set, dynamically determine the API URL based on the current host
function getApiBaseUrl(): string {
  // Check for environment variable first
  if (typeof window !== 'undefined' && (window as any).__NEXT_PUBLIC_API_URL) {
    return (window as any).__NEXT_PUBLIC_API_URL;
  }
  
  const envUrl = (globalThis as any).process?.env?.NEXT_PUBLIC_API_URL;
  if (envUrl && envUrl !== 'undefined') {
    return envUrl;
  }
  
  // In browser, use the current hostname with backend port
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    // Use the same hostname but with backend port 8000
    return `http://${hostname}:8000/api/v1`;
  }
  
  // Fallback for SSR
  return 'http://localhost:8000/api/v1';
}

const API_BASE_URL = getApiBaseUrl();

export interface User {
  id: string;
  email: string;
  name?: string;
  phone?: string;
  phoneVerified: boolean;
  tier: 'free' | 'standard' | 'sniper';
  smsEnabled?: boolean;
  emailEnabled?: boolean;
}

// Token management
const TOKEN_KEY = 'bnb_alerts_token';
const USER_KEY = 'bnb_alerts_user';
const REMEMBER_EMAIL_KEY = 'bnb_alerts_remember_email';
const REMEMBER_PASSWORD_KEY = 'bnb_alerts_remember_password';

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function setUser(user: User): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

// Simple encoding for password storage (not cryptographically secure, but better than plain text)
function encodePassword(password: string): string {
  return btoa(password);
}

function decodePassword(encoded: string): string {
  try {
    return atob(encoded);
  } catch {
    return '';
  }
}

function saveCredentials(email: string, password: string, remember: boolean): void {
  if (remember) {
    localStorage.setItem(REMEMBER_EMAIL_KEY, email);
    localStorage.setItem(REMEMBER_PASSWORD_KEY, encodePassword(password));
  } else {
    localStorage.removeItem(REMEMBER_EMAIL_KEY);
    localStorage.removeItem(REMEMBER_PASSWORD_KEY);
  }
}

function getSavedCredentials(): { email: string; password: string } | null {
  if (typeof window === 'undefined') return null;
  const email = localStorage.getItem(REMEMBER_EMAIL_KEY);
  const encodedPassword = localStorage.getItem(REMEMBER_PASSWORD_KEY);
  
  if (email && encodedPassword) {
    return {
      email,
      password: decodePassword(encodedPassword)
    };
  }
  return null;
}

export const auth = {
  register: async (email: string, password: string, phone: string): Promise<User> => {
    // Sanitize phone number to E.164 format (remove all non-digit chars except leading +)
    const sanitizedPhone = phone.replace(/[^\d+]/g, '').replace(/\+(\d)/g, '+$1');
    
    const response = await fetch(`${API_BASE_URL}/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, phone: sanitizedPhone }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    const data = await response.json();
    // Store user temporarily (without token until phone is verified)
    setUser(data.user);
    return data.user;
  },

  verifyPhone: async (userId: string, code: string): Promise<boolean> => {
    const response = await fetch(`${API_BASE_URL}/auth/verify-phone`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ userId, code }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Verification failed');
    }

    const data = await response.json();
    if (data.success && data.token) {
      setToken(data.token);
      // Update user to mark phone as verified
      const user = auth.getUser();
      if (user) {
        user.phoneVerified = true;
        setUser(user);
      }
      return true;
    }
    return false;
  },

  login: async (email: string, password: string, remember: boolean = false): Promise<User> => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    setToken(data.token);
    setUser(data.user);
    saveCredentials(email, password, remember);
    return data.user;
  },

  logout: async () => {
    const token = getToken();
    if (token) {
      try {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      } catch (error) {
        console.error('Logout request failed:', error);
      }
    }
    removeToken();
    window.location.href = '/';
  },

  getUser: (): User | null => {
    if (typeof window === 'undefined') return null;
    const userStr = localStorage.getItem(USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  },

  getCurrentUser: async (): Promise<User | null> => {
    const token = getToken();
    if (!token) return null;

    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        removeToken();
        return null;
      }

      const user = await response.json();
      setUser(user);
      return user;
    } catch (error) {
      console.error('Failed to get current user:', error);
      removeToken();
      return null;
    }
  },

  isAuthenticated: (): boolean => {
    return getToken() !== null;
  },

  getSavedCredentials: (): { email: string; password: string } | null => {
    return getSavedCredentials();
  },

  clearSavedCredentials: (): void => {
    localStorage.removeItem(REMEMBER_EMAIL_KEY);
    localStorage.removeItem(REMEMBER_PASSWORD_KEY);
  },

  forgotPassword: async (email: string): Promise<{ message: string }> => {
    const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to send reset code');
    }

    const data = await response.json();
    return { message: data.message };
  },

  resetPassword: async (email: string, code: string, newPassword: string): Promise<boolean> => {
    const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, code, newPassword }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to reset password');
    }

    const data = await response.json();
    return data.success;
  },
};
