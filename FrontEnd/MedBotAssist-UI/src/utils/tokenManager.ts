// Token configuration and authentication management
export class TokenManager {
  private static readonly TOKEN_KEY = 'authToken';
  private static readonly DOCTOR_ID_KEY = 'doctorId';
  private static readonly USERNAME_KEY = 'username';
  private static readonly CONVERSATION_ID_KEY = 'conversationId';

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

  // Guardar Conversation ID
  static saveConversationId(conversationId: string) {
    localStorage.setItem(this.CONVERSATION_ID_KEY, conversationId);
  }

  // Obtener Conversation ID
  static getConversationId(): string | null {
    return localStorage.getItem(this.CONVERSATION_ID_KEY);
  }

  // Generar nuevo Conversation ID
  static generateNewConversationId(): string {
    const doctorId = this.getDoctorId() || 'unknown';
    const newConvId = `conv_${doctorId}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.saveConversationId(newConvId);
    return newConvId;
  }

  // Check if the user is authenticated
  static isAuthenticated(): boolean {
    const token = this.getToken();
    return token !== null;
  }

  // Clear all authentication data
  static clearAuthData() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.DOCTOR_ID_KEY);
    localStorage.removeItem(this.USERNAME_KEY);
    localStorage.removeItem(this.CONVERSATION_ID_KEY);
  }

  // Clear only session data (keeps conversation_id for later recovery)
  static clearSessionData() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.DOCTOR_ID_KEY);
    localStorage.removeItem(this.USERNAME_KEY);
    // DO NOT remove CONVERSATION_ID_KEY to allow history recovery
    
    // Emitir evento de logout para que los componentes puedan reaccionar
    window.dispatchEvent(new CustomEvent('userLogout'));
  }

  // Get authorization headers
  static getAuthHeaders(): HeadersInit {
    const token = this.getToken();
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  // Check if the token is about to expire (if backend sends this info)
  static isTokenExpiring(): boolean {
    // Implement expiration logic if backend supports it
    // Por ahora retorna false
    return false;
  }

  // Automatically renew token if possible
  static async renewToken(): Promise<boolean> {
    // Implement if backend has renewal endpoint
    return false;
  }
}

export default TokenManager;
