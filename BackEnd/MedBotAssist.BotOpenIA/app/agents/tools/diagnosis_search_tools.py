"""
Herramientas para búsqueda de pacientes por diagnóstico.
"""

from langchain.tools import Tool
from typing import List, Dict, Any
from app.services.database_service import DatabaseService
from sqlalchemy import text


def search_patients_by_diagnosis_impl(diagnosis_keyword: str, permission_context=None) -> str:
    """
    Search for patients who have a specific medical diagnosis.
    
    Args:
        diagnosis_keyword: Keyword of the diagnosis to search for
        permission_context: User permission context
        
    Returns:
        String with the list of patients who have that diagnosis
    """
    # Validate permissions
    if permission_context:
        if not hasattr(permission_context, 'permissions') or 'read_patients' not in permission_context.permissions:
            return "You do not have permission to search for patients by diagnosis."
    
    try:
        db_service = DatabaseService()
        db_service._ensure_connection()
        
        # 1. SQL query to search for patients by diagnosis in ClinicalSummaries
        query = text("""
        SELECT DISTINCT 
            p.PatientId,
            p.IdentificationNumber,
            p.FullName AS PatientName,
            YEAR(GETDATE()) - YEAR(p.BirthDate) AS Age,
            p.BirthDate,
            p.Phone,
            p.Email,
            cs.Diagnosis,
            cs.Treatment,
            cs.Recommendations
        FROM Patients p
        INNER JOIN Appointments a ON p.PatientId = a.PatientId
        INNER JOIN MedicalNotes mn ON a.AppointmentId = mn.AppointmentId
        INNER JOIN ClinicalSummaries cs ON mn.NoteId = cs.NoteId
        WHERE cs.Diagnosis LIKE :search_pattern
           OR cs.Treatment LIKE :search_pattern
        ORDER BY p.FullName
        """)
        
        # 2. Search parameters
        search_pattern = f"%{diagnosis_keyword}%"
        
        with db_service.engine.connect() as connection:
            result = connection.execute(query, {"search_pattern": search_pattern})
            results = result.fetchall()
        
        if not results:
            return f"No patients found with diagnosis '{diagnosis_keyword}'."
        
        # 3. Format results
        patients_info = []
        for row in results:
            patient_info = (
                f"**{row.PatientName}**\n"
                f"- ID: {row.IdentificationNumber}\n"
                f"- Age: {row.Age} years\n"
                f"- Phone: {row.Phone}\n"
                f"- Email: {row.Email}\n"
                f"- Diagnosis: {row.Diagnosis}\n"
                f"- Treatment: {row.Treatment}\n"
                f"- Recommendations: {row.Recommendations}"
            )
            patients_info.append(patient_info)
        
        response = f"**Patients with diagnosis '{diagnosis_keyword}':**\n\n"
        response += f"**Total found:** {len(results)} patient(s)\n\n"
        response += "\n\n---\n\n".join(patients_info)
        
        return response
        
    except Exception as e:
        error_msg = f"Error searching patients by diagnosis '{diagnosis_keyword}': {str(e)}"
        print(error_msg)
        return f"Error querying patients by diagnosis: {str(e)}"


def get_patient_names_by_diagnosis_impl(diagnosis_keyword: str, permission_context=None) -> str:
    """
    Get only the names and IDs of patients with a specific diagnosis.
    
    Args:
        diagnosis_keyword: Keyword of the diagnosis to search for
        permission_context: User permission context
        
    Returns:
        String with names and IDs of patients who have that diagnosis
    """
    # Validate permissions
    if permission_context:
        if not hasattr(permission_context, 'permissions') or 'read_patients' not in permission_context.permissions:
            return "You do not have permission to query patient information."
    
    try:
        db_service = DatabaseService()
        db_service._ensure_connection()

        # 1. Simplified SQL query to get only names and IDs
        query = text("""
        SELECT DISTINCT 
            p.IdentificationNumber,
            p.FullName AS PatientName,
            cs.Diagnosis
        FROM Patients p
        INNER JOIN Appointments a ON p.PatientId = a.PatientId
        INNER JOIN MedicalNotes mn ON a.AppointmentId = mn.AppointmentId
        INNER JOIN ClinicalSummaries cs ON mn.NoteId = cs.NoteId
        WHERE cs.Diagnosis LIKE :search_pattern
        ORDER BY p.FullName
        """)
        
        # 2. Search parameters
        search_pattern = f"%{diagnosis_keyword}%"
        
        with db_service.engine.connect() as connection:
            result = connection.execute(query, {"search_pattern": search_pattern})
            results = result.fetchall()
        
        if not results:
            return f"No patients found with diagnosis '{diagnosis_keyword}'."
        
        # 3. Format simple results
        if len(results) == 1:
            patient = results[0]
            return f"The patient who suffers from {diagnosis_keyword} is **{patient.PatientName}** with identification **{patient.IdentificationNumber}**."
        else:
            patients_list = []
            for i, patient in enumerate(results, 1):
                patients_list.append(f"{i}. **{patient.PatientName}** (ID: {patient.IdentificationNumber})")
            
            response = f"Patients who suffer from {diagnosis_keyword} are:\n\n"
            response += "\n".join(patients_list)
            response += f"\n\n**Total:** {len(results)} patient(s)"
            
            return response
        
    except Exception as e:
        error_msg = f"Error searching patient names by diagnosis '{diagnosis_keyword}': {str(e)}"
        print(error_msg)
        return f"Error querying patients: {str(e)}"


# Create the tools
search_patients_by_diagnosis = Tool(
    name="search_patients_by_diagnosis",
    description="""
    Search for patients who have a specific medical diagnosis. 
    Returns complete information including contact data, diagnosis, treatment and recommendations.
    
    Parameters:
    - diagnosis_keyword: Diagnosis keyword (e.g., 'Hypertension', 'Diabetes', 'Asthma')
    
    Usage examples:
    - "Search for patients with diabetes"
    - "What patients have hypertension"
    - "Patients diagnosed with asthma"
    """,
    func=search_patients_by_diagnosis_impl
)

get_patient_names_by_diagnosis = Tool(
    name="get_patient_names_by_diagnosis", 
    description="""
    Get only the names and IDs of patients with a specific diagnosis.
    Ideal for answering direct questions about who has certain medical conditions.
    
    Parameters:
    - diagnosis_keyword: Diagnosis keyword (e.g., 'Hypertension', 'Diabetes', 'Asthma')
    
    Usage examples:
    - "What is the name of the patient who suffers from Hypertension?"
    - "Who has diabetes?"
    - "What is the name of the patient with asthma?"
    """,
    func=get_patient_names_by_diagnosis_impl
)
