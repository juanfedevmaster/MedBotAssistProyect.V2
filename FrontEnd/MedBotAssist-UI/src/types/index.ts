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

export interface ClinicalSummary {
    summaryId: number;
    diagnosis: string;
    treatment: string;
    recommendations: string;
    nextSteps: string;
    generatedDate: string;
    medicalNote: MedicalNote;
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
    appointmentId: string;
    patientId: string;
    patientName: string;
    appointmentDate: string;
    appointmentTime: string;
    reason: string;
    status: string;
    notes: string;
}

export interface DoctorInfo {
    medicalLicenseNumber: string;
    specialtyName: string;
    userName: string;
}