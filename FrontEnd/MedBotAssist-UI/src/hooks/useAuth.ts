import { useState, useEffect } from 'react';
import TokenManager from '../utils/tokenManager';

export interface AuthState {
  isAuthenticated: boolean;
  doctorId: string | number | null;
  token: string | null;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    doctorId: null,
    token: null,
  });

  useEffect(() => {
    // Check if authentication data is stored
    const token = TokenManager.getToken();
    const doctorId = TokenManager.getDoctorId();
    
    if (token && doctorId) {
      setAuthState({
        isAuthenticated: true,
        doctorId: doctorId,
        token: token,
      });
    }
  }, []);

  const login = (token: string, doctorId: string | number, username?: string) => {
    TokenManager.saveAuthData(token, doctorId, username);
    
    setAuthState({
      isAuthenticated: true,
      doctorId: doctorId,
      token: token,
    });
  };

  const logout = () => {
    TokenManager.clearSessionData(); // Usar clearSessionData en lugar de clearAuthData
    
    setAuthState({
      isAuthenticated: false,
      doctorId: null,
      token: null,
    });
  };

  const getDoctorId = (): string | number | null => {
    return authState.doctorId || TokenManager.getDoctorId();
  };

  const getToken = (): string | null => {
    return authState.token || TokenManager.getToken();
  };

  const getUsername = (): string | null => {
    return TokenManager.getUsername();
  };

  // Function to get authorization headers
  const getAuthHeaders = (): HeadersInit => {
    return TokenManager.getAuthHeaders();
  };

  // Function to make fetch with automatic authorization
  const authorizedFetch = async (url: string, options: RequestInit = {}): Promise<Response> => {
    const headers = {
      ...getAuthHeaders(),
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    // If we receive 401, the token probably expired
    if (response.status === 401) {
      logout();
      throw new Error('Session expired. Please login again.');
    }

    return response;
  };

  return {
    ...authState,
    login,
    logout,
    getDoctorId,
    getToken,
    getUsername,
    getAuthHeaders,
    authorizedFetch,
  };
};
