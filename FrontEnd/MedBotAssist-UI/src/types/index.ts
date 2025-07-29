export interface UserCredentials {
    username: string;
    password: string;
}

export interface LoginResponse {
    success: boolean;
    message?: string;
    token?: string;
    doctorId: string | number;
    user?: {
        id: string | number;
        username: string;
        email?: string;
    };
}

export interface Doctor {
    id: string | number;
    name: string;
    email?: string;
    specialty?: string;
    licenseNumber?: string;
}

export interface PatientInfoResponseDto {
    patientId: string;
    name: string;
    identificationNumber: string;
    dateOfBirth: string;
    age: number;
    phoneNumber: string;
    email: string;
}

export interface PatientCreateDto {
    name: string;
    identificationNumber: string;
    dateOfBirth: string;
    phoneNumber: string;
    email: string;
}

export interface PatientUpdateDto extends PatientCreateDto {
    patientId: string;
}

export interface MedicalNote {
    noteId: number;
    creationDate: string;
    freeText: string;
    appointmentId: number;
}

export interface MedicalNoteCreateDto {
    noteId: number;
    creationDate: string;
    freeText: string;
    appointmentId: number;
}

export interface ClinicalSummary {
    summaryId: number;
    diagnosis: string;
    treatment: string;
    recommendations: string;
    nextSteps: string;
    generatedDate: string;
    medicalNote: MedicalNote;
}

export interface ClinicalSummaryCreateDto {
    summaryId: number;
    diagnosis: string;
    treatment: string;
    recommendations: string;
    nextSteps: string;
    generatedDate: string;
    medicalNote: MedicalNoteCreateDto;
}

export interface PatientInfoWithClinicalDto {
    clinicalSummaries: ClinicalSummary[];
    patientId: string;
    name: string;
    identificationNumber: string;
    dateOfBirth: string;
    age: number;
    phoneNumber: string;
    email: string;
}

export interface Appointment {
    appointmentId: number;
    patientId: number;
    doctorId: number;
    appointmentDate: string;
    appointmentTime: string;
    status: string;
    notes: string;
    patientName?: string; // Propiedad opcional para compatibilidad
}

export interface DoctorInfo {
    medicalLicenseNumber: string;
    specialtyName: string;
    userName: string;
}