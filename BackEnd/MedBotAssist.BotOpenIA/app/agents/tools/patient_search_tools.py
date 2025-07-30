"""
Patient Search and Query Tools

This module contains all tools related to searching and querying patient information.
All tools in this module require UseAgent + ViewPatients permissions.
"""

from typing import Optional
from langchain.tools import tool
from app.services.database_service import DatabaseService, normalize_text_for_search
from .permission_validators import validate_patient_view_permissions
from datetime import datetime
import logging

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
def search_patients(query: str, top_k: int = 5) -> str:
    """
    Search for patients using natural language queries.
    
    Args:
        query: Natural language query to search for patients
        top_k: Maximum number of results to return (default: 5)
    
    Examples:
    - "patients named Maria"
    - "patients born in 1990"
    - "patients with phone number containing 555"
    - "patients with gmail email"
    
    **Requires Permissions:** UseAgent, ViewPatients
    """
    try:
        # 1. Check permissions
        has_permission, error_msg = validate_patient_view_permissions()
        if not has_permission:
            return error_msg
        
        # 2. Get all patients from database
        patients = get_database_service().get_all_patients()
        
        if not patients:
            return "No patients found in the database"

        # 3. Simple text-based filtering using real database fields with normalization
        normalized_query = normalize_text_for_search(query)
        query_words = normalized_query.split()
        matching_patients = []
        
        for patient in patients:
            # Create searchable text from real patient data and normalize it
            patient_text = f"""
            {patient.get('full_name', '')} 
            {patient.get('identification_number', '')} 
            {patient.get('birth_date', '')}
            {patient.get('phone', '')}
            {patient.get('email', '')}
            """
            normalized_patient_text = normalize_text_for_search(patient_text)
            
            # Check if any query terms match using normalized text
            if any(word in normalized_patient_text for word in query_words):
                matching_patients.append(patient)
        
        if not matching_patients:
            return f"No patients found matching '{query}'"
        
        # 4. Limit results
        limited_patients = matching_patients[:top_k]
        
        # 5. Convert to natural language descriptions
        descriptions = get_database_service().convert_patients_to_natural_language(limited_patients)

        response = f"Found {len(limited_patients)} patients matching '{query}':\n\n"

        for i, description in enumerate(descriptions, 1):
            response += f"{i}. {description}\n\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error searching patients: {e}")
        return f"Error searching patients: {str(e)}"


@tool
def search_patients_by_name(name: str) -> str:
    """
    Search for patients by name (partial matches allowed).
    
    Args:
        name: Patient name to search for
        
    **Requires Permissions:** UseAgent, ViewPatients
    """
    try:
        # 1. Check permissions
        has_permission, error_msg = validate_patient_view_permissions()
        if not has_permission:
            return error_msg

        # 2. Use the database service's search function
        matching_patients = get_database_service().search_patients_by_name(name)
        
        if not matching_patients:
            return f"No patients found with name containing '{name}'"
        
        # 3. Convert to natural language descriptions
        descriptions = get_database_service().convert_patients_to_natural_language(matching_patients)

        response = f"Found {len(matching_patients)} patient(s) with name containing '{name}':\n\n"
        
        for i, description in enumerate(descriptions, 1):
            response += f"{i}. {description}\n\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error searching patients by name: {e}")
        return f"Error searching patients: {str(e)}"


@tool
def search_patients_by_condition(contact_info: str) -> str:
    """
    Search for patients by contact information (phone or email).
    Since medical conditions are not available in the current database,
    this tool searches by contact information instead.
    
    Args:
        contact_info: Phone number or email to search for (partial matches allowed)
        
    **Requires Permissions:** UseAgent, ViewPatients
    """
    try:
        # 1. Check permissions
        has_permission, error_msg = validate_patient_view_permissions()
        if not has_permission:
            return error_msg
        
        patients = get_database_service().get_all_patients()
        
        if not patients:
            return "No patients found in the database"
        
        # 2. Filter by phone or email with normalization for better matching
        normalized_contact = normalize_text_for_search(contact_info)
        matching_patients = []
        
        for patient in patients:
            phone = normalize_text_for_search(patient.get('phone', ''))
            email = normalize_text_for_search(patient.get('email', ''))
            
            if normalized_contact in phone or normalized_contact in email:
                matching_patients.append(patient)
        
        if not matching_patients:
            return f"No patients found with contact info containing '{contact_info}'"
        
        # 3. Convert to natural language descriptions
        descriptions = get_database_service().convert_patients_to_natural_language(matching_patients)
        
        response = f"Found {len(matching_patients)} patient(s) with contact info containing '{contact_info}':\n\n"
        
        for i, description in enumerate(descriptions, 1):
            response += f"{i}. {description}\n\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error searching patients by contact info: {e}")
        return f"Error searching patients by contact info: {str(e)}"


@tool
def get_patient_by_id(identification_number: str) -> str:
    """
    Get detailed information for a specific patient by their identification number.
    
    Args:
        identification_number: Patient's identification number (exact match)
        
    **Requires Permissions:** UseAgent, ViewPatients
    """
    try:
        # 1. Check permissions
        has_permission, error_msg = validate_patient_view_permissions()
        if not has_permission:
            return error_msg
        
        patients = get_database_service().get_all_patients()
        
        if not patients:
            return "No patients found in the database"
        
        # 2. Search for patient with exact identification number match
        matching_patient = None
        for patient in patients:
            if patient.get('identification_number') == identification_number:
                matching_patient = patient
                break
        
        if not matching_patient:
            return f"No patient found with identification number '{identification_number}'"
        
        # Convert to natural language description
        descriptions = get_database_service().convert_patients_to_natural_language([matching_patient])
        
        if descriptions:
            response = f"**Patient Details for ID: {identification_number}**\n\n"
            response += descriptions[0]
            
            # Add additional details if available
            if matching_patient.get('birth_date'):
                try:
                    birth_date = datetime.fromisoformat(matching_patient['birth_date'].replace('Z', '+00:00'))
                    today = datetime.now()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    response += f"  - Calculated Age: {age} years\n"
                    response += f"  - Phone: {matching_patient.get('phone', 'N/A')}\n"
                except:
                    pass
            
            return response
        else:
            return f"Error processing patient information for ID '{identification_number}'"

    except Exception as e:
        logger.error(f"Error getting patient by ID: {e}")
        return f"Error retrieving patient information: {str(e)}"


@tool
def get_patients_summary() -> str:
    """
    Get a summary of all patients in the database.
    
    Returns only the total count of patients, without individual patient details.
    For detailed patient information, use search tools with specific criteria.
    
    **Requires Permissions:** UseAgent, ViewPatients
    """
    try:
        # 1. Check permissions
        has_permission, error_msg = validate_patient_view_permissions()
        if not has_permission:
            return error_msg
        
        patients = get_database_service().get_all_patients()
        
        if not patients:
            return "No patients found in the database"
        
        # 2. Calculate basic statistics from real data
        total_patients = len(patients)
        patients_with_email = sum(1 for p in patients if p.get('email'))
        patients_with_phone = sum(1 for p in patients if p.get('phone'))
        patients_with_id = sum(1 for p in patients if p.get('identification_number'))
        
        # 3. Calculate age distribution from birth dates
        ages = []
        for patient in patients:
            if patient.get('birth_date'):
                try:
                    birth_date = datetime.fromisoformat(patient['birth_date'].replace('Z', '+00:00'))
                    today = datetime.now()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    ages.append(age)
                except:
                    pass
        
        avg_age = sum(ages) / len(ages) if ages else 0
        min_age = min(ages) if ages else 0
        max_age = max(ages) if ages else 0
        
        response = f"**Database Summary**\n\n"
        response += f"**Total Patients:** {total_patients}\n"
        response += f"**Contact Information:**\n"
        response += f"  - With Email: {patients_with_email}\n"
        response += f"  - With Phone: {patients_with_phone}\n"
        response += f"  - With ID Number: {patients_with_id}\n\n"
        
        if ages:
            response += f"**Age Statistics:**\n"
            response += f"  - Average Age: {avg_age:.1f} years\n"
            response += f"  - Age Range: {min_age} - {max_age} years\n"
            response += f"  - Patients with birth date: {len(ages)}\n\n"
        
        response += f"**Nota:** For detailed information on specific patients, provide an identification number (IdentificationNumber) or use the specific search tools."
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting patients summary: {e}")
        return f"Error getting patients summary: {str(e)}"


@tool
def filter_patients_by_demographics(age_min: Optional[int] = None, 
                                  age_max: Optional[int] = None,
                                  email_domain: Optional[str] = None,
                                  year_of_birth: Optional[int] = None) -> str:
    """
    Filter patients by available demographic criteria based on real database fields.
    
    Args:
        age_min: Minimum age filter
        age_max: Maximum age filter  
        email_domain: Email domain filter (e.g., gmail.com)
        year_of_birth: Year of birth filter
        
    **Requires Permissions:** UseAgent, ViewPatients
    """
    try:
        # 1. Check permissions
        has_permission, error_msg = validate_patient_view_permissions()
        if not has_permission:
            return error_msg
        
        patients = get_database_service().get_all_patients()
        
        if not patients:
            return "No patients found in the database"
        
        filtered_patients = patients.copy()
        
        # 2. Age filtering
        if age_min is not None or age_max is not None:
            age_filtered = []
            for patient in filtered_patients:
                if patient.get('birth_date'):
                    try:
                        birth_date = datetime.fromisoformat(patient['birth_date'].replace('Z', '+00:00'))
                        today = datetime.now()
                        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                        
                        if age_min is not None and age < age_min:
                            continue
                        if age_max is not None and age > age_max:
                            continue
                        
                        age_filtered.append(patient)
                    except:
                        pass
            filtered_patients = age_filtered
        
        # 3. Email domain filtering with normalization
        if email_domain:
            normalized_domain = normalize_text_for_search(email_domain)
            filtered_patients = [
                p for p in filtered_patients 
                if normalize_text_for_search(p.get('email', '')).endswith(normalized_domain)
            ]
        
        # 4. Year of birth filtering
        if year_of_birth:
            birth_year_filtered = []
            for patient in filtered_patients:
                if patient.get('birth_date'):
                    try:
                        birth_date = datetime.fromisoformat(patient['birth_date'].replace('Z', '+00:00'))
                        if birth_date.year == year_of_birth:
                            birth_year_filtered.append(patient)
                    except:
                        pass
            filtered_patients = birth_year_filtered
        
        if not filtered_patients:
            return f"No patients found matching the specified criteria"
        
        # 5. Build filter description
        filters = []
        if age_min is not None:
            filters.append(f"age >= {age_min}")
        if age_max is not None:
            filters.append(f"age <= {age_max}")
        if email_domain:
            filters.append(f"email domain: {email_domain}")
        if year_of_birth:
            filters.append(f"born in: {year_of_birth}")
        
        filter_desc = ", ".join(filters)
        
        # 6. Convert to natural language descriptions
        descriptions = get_database_service().convert_patients_to_natural_language(filtered_patients)

        response = f"Found {len(filtered_patients)} patient(s) matching criteria: {filter_desc}\n\n"

        for i, description in enumerate(descriptions, 1):
            response += f"{i}. {description}\n\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error filtering patients: {e}")
        return f"Error filtering patients: {str(e)}"
