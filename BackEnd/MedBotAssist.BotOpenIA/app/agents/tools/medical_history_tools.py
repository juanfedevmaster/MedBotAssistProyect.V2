from langchain.tools import tool
from app.services.database_service import DatabaseService
from app.agents.tools.permission_validators import validate_patient_view_permissions
from sqlalchemy import text
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize the database service lazily
database_service = None

def get_database_service():
    """Get or create database service instance."""
    global database_service
    if database_service is None:
        database_service = DatabaseService()
    return database_service


@tool
def get_patient_medical_history(identification_number: str) -> str:
    """
    Retrieve comprehensive medical history including appointments, diagnoses, and clinical summaries for a patient.
    
    Args:
        identification_number: Patient's identification number
        
    Returns:
        Natural language summary of the patient's medical history, appointments, and diagnoses
        
    Requires: ViewPatients permission
    """
    try:
        # Validate permissions first
        if not validate_patient_view_permissions():
            return "Error: You do not have sufficient permissions to access patient medical history. ViewPatients permission is required."
        
        db = get_database_service()
        db._ensure_connection()
        
        query = text("""
            SELECT 
                -- Información del paciente
                p.PatientId,
                p.FullName AS PatientName,
                p.IdentificationNumber,
                p.BirthDate,
                p.Phone,
                p.Email,

                -- Información de las citas
                a.AppointmentId,
                a.AppointmentDate,
                a.AppointmentTime,
                a.Status,
                a.Notes AS AppointmentNotes,

                -- Información del doctor
                d.DoctorId,
                u.FullName AS DoctorName,
                s.SpecialtyName AS DoctorSpecialty,

                -- Nota médica
                mn.NoteId,
                mn.CreationDate AS NoteDate,
                mn.[FreeText] AS MedicalNote,

                -- Resumen clínico generado por IA
                cs.SummaryId,
                cs.Diagnosis,
                cs.Treatment,
                cs.Recommendations,
                cs.NextSteps,
                cs.GeneratedDate AS SummaryDate

            FROM Patients p
            LEFT JOIN Appointments a ON p.PatientId = a.PatientId
            LEFT JOIN Doctors d ON a.DoctorId = d.DoctorId
            LEFT JOIN Users u ON d.UserId = u.UserId
            LEFT JOIN Specialties s ON d.SpecialtyId = s.SpecialtyId
            LEFT JOIN MedicalNotes mn ON a.AppointmentId = mn.AppointmentId
            LEFT JOIN ClinicalSummaries cs ON mn.NoteId = cs.NoteId

            WHERE p.IdentificationNumber = :identification_number
            ORDER BY a.AppointmentDate DESC, a.AppointmentTime DESC
        """)
        
        with db.engine.connect() as conn:
            result = conn.execute(query, {"identification_number": identification_number})
            rows = result.fetchall()
            
            if not rows:
                return f"No patient found with identification number '{identification_number}'."
            
            # Process the results
            medical_history = _process_medical_history_data(rows)
            
            logger.info(f"Retrieved medical history for patient '{identification_number}'")
            return medical_history
            
    except Exception as e:
        logger.error(f"Error retrieving medical history for patient '{identification_number}': {e}")
        return f"Error accessing medical history: {str(e)}"


@tool 
def get_patient_diagnoses_summary(identification_number: str) -> str:
    """
    Get a focused summary of patient's diagnoses and treatments from clinical summaries.
    
    Args:
        identification_number: Patient's identification number
        
    Returns:
        Natural language summary focused on diagnoses and treatments
        
    Requires: ViewPatients permission
    """
    try:
        # Validate permissions first
        if not validate_patient_view_permissions():
            return "Error: You do not have sufficient permissions to access patient diagnoses. ViewPatients permission is required."
        
        db = get_database_service()
        db._ensure_connection()
        
        query = text("""
            SELECT 
                p.FullName AS PatientName,
                p.IdentificationNumber,
                a.AppointmentDate,
                u.FullName AS DoctorName,
                s.SpecialtyName AS DoctorSpecialty,
                cs.Diagnosis,
                cs.Treatment,
                cs.Recommendations,
                cs.NextSteps,
                cs.GeneratedDate AS SummaryDate

            FROM Patients p
            LEFT JOIN Appointments a ON p.PatientId = a.PatientId
            LEFT JOIN Doctors d ON a.DoctorId = d.DoctorId
            LEFT JOIN Users u ON d.UserId = u.UserId
            LEFT JOIN Specialties s ON d.SpecialtyId = s.SpecialtyId
            LEFT JOIN MedicalNotes mn ON a.AppointmentId = mn.AppointmentId
            LEFT JOIN ClinicalSummaries cs ON mn.NoteId = cs.NoteId

            WHERE p.IdentificationNumber = :identification_number
            AND cs.Diagnosis IS NOT NULL
            ORDER BY a.AppointmentDate DESC, a.AppointmentTime DESC
        """)
        
        with db.engine.connect() as conn:
            result = conn.execute(query, {"identification_number": identification_number})
            rows = result.fetchall()
            
            if not rows:
                return f"No diagnoses found for patient with identification '{identification_number}'."
            
            # Process the diagnoses data
            diagnoses_summary = _process_diagnoses_data(rows)
            
            logger.info(f"Retrieved diagnoses summary for patient '{identification_number}'")
            return diagnoses_summary
            
    except Exception as e:
        logger.error(f"Error retrieving diagnoses for patient '{identification_number}': {e}")
        return f"Error accessing diagnoses: {str(e)}"


@tool
def count_patients_by_diagnosis(diagnosis_keyword: str) -> str:
    """
    Count how many patients have a specific diagnosis or diagnosis containing a keyword.
    
    Args:
        diagnosis_keyword: Keyword to search for in diagnoses (partial matches allowed)
        
    Returns:
        Natural language summary with the count of patients having that diagnosis
        
    Requires: ViewPatients permission
    """
    try:
        # Validate permissions first
        if not validate_patient_view_permissions():
            return "Error: You do not have sufficient permissions to access patient diagnoses. ViewPatients permission is required."
        
        db = get_database_service()
        db._ensure_connection()
        
        query = text("""
            SELECT 
                COUNT(DISTINCT p.PatientId) AS PatientCount,
                COUNT(cs.Diagnosis) AS DiagnosisCount,
                cs.Diagnosis
            FROM Patients p
            LEFT JOIN Appointments a ON p.PatientId = a.PatientId
            LEFT JOIN Doctors d ON a.DoctorId = d.DoctorId
            LEFT JOIN Users u ON d.UserId = u.UserId
            LEFT JOIN Specialties s ON d.SpecialtyId = s.SpecialtyId
            LEFT JOIN MedicalNotes mn ON a.AppointmentId = mn.AppointmentId
            LEFT JOIN ClinicalSummaries cs ON mn.NoteId = cs.NoteId
            WHERE cs.Diagnosis IS NOT NULL 
            AND LOWER(cs.Diagnosis) LIKE LOWER(:diagnosis_pattern)
            GROUP BY cs.Diagnosis
            ORDER BY PatientCount DESC, cs.Diagnosis
        """)
        
        with db.engine.connect() as conn:
            result = conn.execute(query, {"diagnosis_pattern": f"%{diagnosis_keyword}%"})
            rows = result.fetchall()
            
            if not rows:
                return f"No patients found with diagnoses containing '{diagnosis_keyword}'."
            
            # Process the diagnosis count data
            diagnosis_count_summary = _process_diagnosis_count_data(rows, diagnosis_keyword)
            
            logger.info(f"Retrieved diagnosis count for keyword '{diagnosis_keyword}'")
            return diagnosis_count_summary
            
    except Exception as e:
        logger.error(f"Error counting patients by diagnosis '{diagnosis_keyword}': {e}")
        return f"Error accessing diagnosis count: {str(e)}"


def _process_medical_history_data(rows: List[Any]) -> str:
    """Process medical history database results into natural language."""
    if not rows:
        return "No medical information found."
    
    # Get patient info from first row
    first_row = rows[0]
    patient_name = first_row.PatientName
    patient_id = first_row.IdentificationNumber
    
    # Calculate age if birth date is available
    age_text = ""
    if first_row.BirthDate:
        try:
            birth_date = first_row.BirthDate
            if isinstance(birth_date, str):
                birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
            
            today = datetime.now().date()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            age_text = f", {age} years old"
        except:
            pass
    
    result = f"**Complete Medical History**\n\n"
    result += f"**Patient:** {patient_name} (ID: {patient_id}){age_text}\n\n"
    
    # Group appointments and medical data
    appointments = {}
    
    for row in rows:
        if row.AppointmentId:
            appointment_key = f"{row.AppointmentId}"
            if appointment_key not in appointments:
                appointments[appointment_key] = {
                    'date': row.AppointmentDate,
                    'time': row.AppointmentTime,
                    'status': row.Status,
                    'notes': row.AppointmentNotes,
                    'doctor': row.DoctorName,
                    'specialty': row.DoctorSpecialty,
                    'medical_notes': [],
                    'clinical_summaries': []
                }
            
            # Add medical note if exists
            if row.MedicalNote and row.MedicalNote not in [note['text'] for note in appointments[appointment_key]['medical_notes']]:
                appointments[appointment_key]['medical_notes'].append({
                    'date': row.NoteDate,
                    'text': row.MedicalNote
                })
            
            # Add clinical summary if exists
            if row.Diagnosis and not any(cs['diagnosis'] == row.Diagnosis for cs in appointments[appointment_key]['clinical_summaries']):
                appointments[appointment_key]['clinical_summaries'].append({
                    'diagnosis': row.Diagnosis,
                    'treatment': row.Treatment,
                    'recommendations': row.Recommendations,
                    'next_steps': row.NextSteps,
                    'date': row.SummaryDate
                })
    
    if not appointments:
        result += "No medical appointments found.\n"
        return result
    
    result += f"**Total medical appointments:** {len(appointments)}\n\n"
    
    # Process each appointment
    for i, (appointment_id, appointment_data) in enumerate(appointments.items(), 1):
        result += f"## Appointment #{i}\n"
        result += f"**Date:** {appointment_data['date']}\n"
        if appointment_data['time']:
            result += f"**Time:** {appointment_data['time']}\n"
        result += f"**Status:** {appointment_data['status']}\n"
        
        if appointment_data['doctor']:
            result += f"**Doctor:** Dr. {appointment_data['doctor']}"
            if appointment_data['specialty']:
                result += f" ({appointment_data['specialty']})"
            result += "\n"
        
        if appointment_data['notes']:
            result += f"**Appointment notes:** {appointment_data['notes']}\n"
        
        # Add medical notes
        if appointment_data['medical_notes']:
            result += "\n### Medical Notes:\n"
            for note in appointment_data['medical_notes']:
                result += f"- **{note['date']}:** {note['text']}\n"
        
        # Add clinical summaries
        if appointment_data['clinical_summaries']:
            result += "\n### Clinical Summary:\n"
            for summary in appointment_data['clinical_summaries']:
                if summary['diagnosis']:
                    result += f"**Diagnosis:** {summary['diagnosis']}\n"
                if summary['treatment']:
                    result += f"**Treatment:** {summary['treatment']}\n"
                if summary['recommendations']:
                    result += f"**Recommendations:** {summary['recommendations']}\n"
                if summary['next_steps']:
                    result += f"**Next steps:** {summary['next_steps']}\n"
        
        result += "\n---\n\n"
    
    return result


def _process_diagnoses_data(rows: List[Any]) -> str:
    """Process diagnoses database results into natural language."""
    if not rows:
        return "No diagnoses found."
    
    # Get patient info from first row
    first_row = rows[0]
    patient_name = first_row.PatientName
    patient_id = first_row.IdentificationNumber
    
    result = f"**Diagnoses Summary**\n\n"
    result += f"**Patient:** {patient_name} (ID: {patient_id})\n\n"
    
    # Process each diagnosis
    diagnoses = []
    for row in rows:
        diagnosis_info = {
            'date': row.AppointmentDate,
            'doctor': row.DoctorName,
            'specialty': row.DoctorSpecialty,
            'diagnosis': row.Diagnosis,
            'treatment': row.Treatment,
            'recommendations': row.Recommendations,
            'next_steps': row.NextSteps
        }
        diagnoses.append(diagnosis_info)
    
    result += f"**Total diagnoses found:** {len(diagnoses)}\n\n"
    
    for i, diagnosis in enumerate(diagnoses, 1):
        result += f"## Diagnosis #{i}\n"
        result += f"**Date:** {diagnosis['date']}\n"
        
        if diagnosis['doctor']:
            result += f"**Doctor:** Dr. {diagnosis['doctor']}"
            if diagnosis['specialty']:
                result += f" ({diagnosis['specialty']})"
            result += "\n"
        
        result += f"**Diagnosis:** {diagnosis['diagnosis']}\n"
        
        if diagnosis['treatment']:
            result += f"**Treatment:** {diagnosis['treatment']}\n"
        
        if diagnosis['recommendations']:
            result += f"**Recommendations:** {diagnosis['recommendations']}\n"
        
        if diagnosis['next_steps']:
            result += f"**Next steps:** {diagnosis['next_steps']}\n"
        
        result += "\n---\n\n"
    
    return result


def _process_diagnosis_count_data(rows: List[Any], diagnosis_keyword: str) -> str:
    """Process diagnosis count database results into natural language."""
    if not rows:
        return f"No diagnoses found containing '{diagnosis_keyword}'."
    
    result = f"**Patient Count by Diagnosis**\n\n"
    result += f"**Search:** Diagnoses containing '{diagnosis_keyword}'\n\n"
    
    total_patients = sum(row.PatientCount for row in rows)
    total_diagnoses = sum(row.DiagnosisCount for row in rows)
    unique_diagnoses = len(rows)
    
    result += f"**General Summary:**\n"
    result += f"- **Total unique patients:** {total_patients}\n"
    result += f"- **Total diagnoses recorded:** {total_diagnoses}\n"
    result += f"- **Different diagnosis types:** {unique_diagnoses}\n\n"
    
    result += f"**Breakdown by Diagnosis:**\n\n"
    
    for i, row in enumerate(rows, 1):
        result += f"## {i}. {row.Diagnosis}\n"
        result += f"- **Affected patients:** {row.PatientCount}\n"
        result += f"- **Times diagnosed:** {row.DiagnosisCount}\n"
        
        # Calculate percentage
        percentage = (row.PatientCount / total_patients * 100) if total_patients > 0 else 0
        result += f"- **Percentage:** {percentage:.1f}% of patients with related diagnoses\n\n"
    
    result += f"---\n\n"
    result += f"**Note:** Counts show unique patients per diagnosis. A patient may have multiple diagnoses."
    
    return result
