import { API_ENDPOINTS } from '../config/endpoints';
import TokenManager from '../utils/tokenManager';

export class ApiService {
  
  private static async handleResponse(response: Response) {
    if (response.status === 401) {
      // Token expired or invalid
      TokenManager.clearAuthData();
      window.location.href = '/';
      throw new Error('Session expired. Please login again.');
    }

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response;
  }

  // Generic method for making authenticated requests
  static async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const headers = {
      ...TokenManager.getAuthHeaders(),
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    return this.handleResponse(response);
  }

  // Specific methods for each endpoint
  static async login(credentials: { userName: string; password: string }) {
    const response = await fetch(API_ENDPOINTS.LOGIN, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    // Handle login errors differently - don't redirect on 401
    if (response.status === 401) {
      throw new Error('Invalid username or password. Please check your credentials and try again.');
    }

    if (!response.ok) {
      throw new Error(`Login failed. Please try again.`);
    }

    return response;
  }

  static async register(userData: any) {
    const response = await fetch(API_ENDPOINTS.REGISTER, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    return this.handleResponse(response);
  }

  static async getAllPatients() {
    return this.authenticatedFetch(API_ENDPOINTS.PATIENTS_GET_ALL);
  }

  static async getPatientById(patientId: string | number) {
    return this.authenticatedFetch(API_ENDPOINTS.PATIENTS_GET_BY_ID(patientId));
  }

  static async createPatient(patientData: any) {
    return this.authenticatedFetch(API_ENDPOINTS.PATIENTS_CREATE, {
      method: 'POST',
      body: JSON.stringify(patientData),
    });
  }

  static async updatePatient(patientId: string | number, patientData: any) {
    return this.authenticatedFetch(API_ENDPOINTS.PATIENTS_UPDATE(patientId), {
      method: 'PUT',
      body: JSON.stringify(patientData),
    });
  }

  static async createMedicalNote(noteData: any) {
    return this.authenticatedFetch(API_ENDPOINTS.MEDICAL_NOTE_CREATE, {
      method: 'POST',
      body: JSON.stringify(noteData),
    });
  }

  static async createClinicalSummary(summaryData: any) {
    return this.authenticatedFetch(API_ENDPOINTS.MEDICAL_NOTE_CREATE, {
      method: 'POST',
      body: JSON.stringify(summaryData),
    });
  }

  static async getAppointmentsByDoctor(doctorId: string | number) {
    return this.authenticatedFetch(API_ENDPOINTS.APPOINTMENTS_GET_BY_DOCTOR(doctorId));
  }

  static async createAppointment(appointmentData: any) {
    const headers = {
      ...TokenManager.getAuthHeaders(),
      'Content-Type': 'application/json',
    };

    const response = await fetch(API_ENDPOINTS.APPOINTMENTS_CREATE, {
      method: 'POST',
      headers,
      body: JSON.stringify(appointmentData),
    });

    // Don't handle 409 here - let the calling component handle it
    if (response.status === 401) {
      TokenManager.clearAuthData();
      window.location.href = '/';
      throw new Error('Session expired. Please login again.');
    }

    // Return response as-is for 409 and other status codes
    // Let the calling component handle them appropriately
    return response;
  }

  static async updateAppointment(appointmentId: string | number, appointmentData: any) {
    const headers = {
      ...TokenManager.getAuthHeaders(),
      'Content-Type': 'application/json',
    };

    const response = await fetch(API_ENDPOINTS.APPOINTMENTS_UPDATE(appointmentId), {
      method: 'PUT',
      headers,
      body: JSON.stringify(appointmentData),
    });

    // Don't handle 409 here - let the calling component handle it
    if (response.status === 401) {
      TokenManager.clearAuthData();
      window.location.href = '/';
      throw new Error('Session expired. Please login again.');
    }

    // Return response as-is for 409 and other status codes
    // Let the calling component handle them appropriately
    return response;
  }

  // Method to check if the token is still valid
  static async validateToken(): Promise<boolean> {
    if (!TokenManager.isAuthenticated()) return false;

    try {
      // Try to make a request that requires authentication
      const response = await this.authenticatedFetch(API_ENDPOINTS.HOME);
      return response.ok;
    } catch (error) {
      return false;
    }
  }

  // Method to refresh the token (if the backend supports it)
  static async refreshToken(): Promise<boolean> {
    // Implementar si el backend tiene endpoint de refresh
    // Por ahora retorna false
    return false;
  }

  // Specific method for AI API requests with mandatory token
  static async aiApiFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const token = TokenManager.getToken();
    
    if (!token) {
      throw new Error('Authentication required for AI API');
    }

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    return this.handleResponse(response);
  }
}

export default ApiService;
