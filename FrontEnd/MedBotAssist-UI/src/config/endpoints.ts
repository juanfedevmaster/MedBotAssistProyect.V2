// Get environment variables with fallbacks
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5098';
const AI_API_BASE_URL = process.env.REACT_APP_AI_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}${process.env.REACT_APP_AUTH_LOGIN_ENDPOINT || '/api/Auth/login'}`,
  HOME: process.env.REACT_APP_HOME_ENDPOINT || '/api/home',
  REGISTER: `${API_BASE_URL}${process.env.REACT_APP_AUTH_REGISTER_ENDPOINT || '/api/Auth/register'}`,
  PATIENTS_GET_ALL: `${API_BASE_URL}${process.env.REACT_APP_PATIENTS_GET_ALL_ENDPOINT || '/api/Patient/getAll'}`,
  PATIENTS_GET_BY_ID: (id: string | number) => `${API_BASE_URL}${process.env.REACT_APP_PATIENTS_GET_BY_ID_ENDPOINT || '/api/Patient/getInfo'}?patientId=${id}`,
  PATIENTS_CREATE: `${API_BASE_URL}${process.env.REACT_APP_PATIENTS_CREATE_ENDPOINT || '/api/Patient/create'}`,
  PATIENTS_UPDATE: (id: string | number) => `${API_BASE_URL}${process.env.REACT_APP_PATIENTS_UPDATE_ENDPOINT || '/api/Patient/update'}/${id}`,
  // Appointment endpoints
  APPOINTMENTS_GET_BY_DOCTOR: (doctorId: string | number) => `${API_BASE_URL}${process.env.REACT_APP_APPOINTMENTS_GET_BY_DOCTOR_ENDPOINT || '/api/Appointment/getByDoctor'}/${doctorId}`,
  // AI Chat endpoints
  AI_CHAT: `${AI_API_BASE_URL}${process.env.REACT_APP_AI_CHAT_ENDPOINT || '/api/v1/agent/chat'}`
};