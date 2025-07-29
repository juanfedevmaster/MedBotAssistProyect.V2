// Get environment variables with fallbacks
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5098';
const AI_API_BASE_URL = process.env.REACT_APP_AI_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}${process.env.REACT_APP_AUTH_LOGIN_ENDPOINT || '/api/Auth/login'}`,
  HOME: process.env.REACT_APP_HOME_ENDPOINT || '/api/home',
  REGISTER: `${API_BASE_URL}${process.env.REACT_APP_AUTH_REGISTER_ENDPOINT || '/api/Auth/register'}`,
  REGISTER_SPECIALTIES: `${API_BASE_URL}${process.env.REACT_APP_AUTH_REGISTER_SPECIALTIES_ENDPOINT || '/api/Auth/register'}`,
  PATIENTS_GET_ALL: `${API_BASE_URL}${process.env.REACT_APP_PATIENTS_GET_ALL_ENDPOINT || '/api/Patient/getAll'}`,
  PATIENTS_GET_BY_ID: (id: string | number) => `${API_BASE_URL}${process.env.REACT_APP_PATIENTS_GET_BY_ID_ENDPOINT || '/api/Patient/getInfo'}?patientId=${id}`,
  PATIENTS_CREATE: `${API_BASE_URL}${process.env.REACT_APP_PATIENTS_CREATE_ENDPOINT || '/api/Patient/create'}`,
  PATIENTS_UPDATE: (id: string | number) => `${API_BASE_URL}${process.env.REACT_APP_PATIENTS_UPDATE_ENDPOINT || '/api/Patient/update'}/${id}`,
  // Appointment endpoints
  APPOINTMENTS_GET_BY_DOCTOR: (doctorId: string | number) => `${API_BASE_URL}${process.env.REACT_APP_APPOINTMENTS_GET_BY_DOCTOR_ENDPOINT || '/api/Appointment/getByDoctor'}/${doctorId}`,
  APPOINTMENTS_CREATE: `${API_BASE_URL}${process.env.REACT_APP_APPOINTMENTS_CREATE_ENDPOINT || '/api/Appointment/create'}`,
  APPOINTMENTS_UPDATE: (appointmentId: string | number) => `${API_BASE_URL}${process.env.REACT_APP_APPOINTMENTS_UPDATE_ENDPOINT || '/api/Appointment/update'}/${appointmentId}`,
  // Medical Note endpoints
  MEDICAL_NOTE_CREATE: `${API_BASE_URL}${process.env.REACT_APP_MEDICAL_NOTE_CREATE_ENDPOINT || '/api/MedicalNote/CreateMedicalNote'}`,
  // AI Chat endpoints
  AI_CHAT: `${AI_API_BASE_URL}${process.env.REACT_APP_AI_CHAT_ENDPOINT || '/api/v1/agent/chat'}`
};