// Configuración del token y manejo de autenticación
export class TokenManager {
  private static readonly TOKEN_KEY = 'authToken';
  private static readonly DOCTOR_ID_KEY = 'doctorId';
  private static readonly USERNAME_KEY = 'username';

  // Guardar token y datos de usuario
  static saveAuthData(token: string, doctorId: string | number, username?: string) {
    localStorage.setItem(this.TOKEN_KEY, token);
    localStorage.setItem(this.DOCTOR_ID_KEY, doctorId.toString());
    if (username) {
      localStorage.setItem(this.USERNAME_KEY, username);
    }
  }

  // Obtener token
  static getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  // Obtener Doctor ID
  static getDoctorId(): string | null {
    return localStorage.getItem(this.DOCTOR_ID_KEY);
  }

  // Obtener Username
  static getUsername(): string | null {
    return localStorage.getItem(this.USERNAME_KEY);
  }

  // Verificar si el usuario está autenticado
  static isAuthenticated(): boolean {
    const token = this.getToken();
    return token !== null;
  }

  // Limpiar todos los datos de autenticación
  static clearAuthData() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.DOCTOR_ID_KEY);
    localStorage.removeItem(this.USERNAME_KEY);
  }

  // Obtener headers de autorización
  static getAuthHeaders(): HeadersInit {
    const token = this.getToken();
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  // Verificar si el token está próximo a expirar (si el backend envía esta info)
  static isTokenExpiring(): boolean {
    // Implementar lógica de expiración si el backend lo soporta
    // Por ahora retorna false
    return false;
  }

  // Renovar token automáticamente si es posible
  static async renewToken(): Promise<boolean> {
    // Implementar si el backend tiene endpoint de renovación
    return false;
  }
}

export default TokenManager;
