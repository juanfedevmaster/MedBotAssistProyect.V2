from typing import List, Dict, Any, Optional
from langchain.tools import tool
from app.services.database_service import DatabaseService, normalize_text_for_search
from app.services.permission_context import permission_context
from app.core.config import settings
import logging
import httpx
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# Initialize the database service
database_service = DatabaseService()

def check_view_patients_permission() -> tuple[bool, str]:
    """
    Check if the current user has ViewPatients permission.
    
    Returns:
        tuple: (has_permission, error_message_if_not)
    """
    if not permission_context.has_permission("ViewPatients"):
        username = permission_context.get_username() or "Unknown"
        permissions = permission_context.get_permissions()
        
        error_msg = f"""🚫 **Acceso Denegado**

El usuario '{username}' no tiene permisos para acceder a información de pacientes.

**Permisos actuales:** {', '.join(permissions) if permissions else 'Ninguno'}
**Permiso requerido:** ViewPatients

Por favor, contacte al administrador del sistema para obtener los permisos necesarios."""
        
        return False, error_msg
    
    return True, ""

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
    
    **Requires Permission:** ViewPatients
    """
    try:
        # Check ViewPatients permission
        has_permission, error_msg = check_view_patients_permission()
        if not has_permission:
            return error_msg
        
        # Get all patients from database
        patients = database_service.get_all_patients()
        
        if not patients:
            return "📊 No patients found in the database"
        
        # Simple text-based filtering using real database fields with normalization
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
            return f"🔍 No patients found matching '{query}'"
        
        # Limit results
        limited_patients = matching_patients[:top_k]
        
        # Convert to natural language descriptions
        descriptions = database_service.convert_patients_to_natural_language(limited_patients)
        
        response = f"🔍 Found {len(limited_patients)} patients matching '{query}':\n\n"
        
        for i, description in enumerate(descriptions, 1):
            response += f"{i}. {description}\n\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error searching patients: {e}")
        return f"❌ Error searching patients: {str(e)}"

@tool
def get_patient_by_id(identification_number: str) -> str:
    """
    Get detailed information for a specific patient by their identification number.
    
    Args:
        identification_number: Patient's identification number (exact match)
        
    **Requires Permission:** ViewPatients
    """
    try:
        # Check ViewPatients permission
        has_permission, error_msg = check_view_patients_permission()
        if not has_permission:
            return error_msg
        
        patients = database_service.get_all_patients()
        
        if not patients:
            return "📊 No patients found in the database"
        
        # Search for patient with exact identification number match
        matching_patient = None
        for patient in patients:
            if patient.get('identification_number') == identification_number:
                matching_patient = patient
                break
        
        if not matching_patient:
            return f"🔍 No patient found with identification number '{identification_number}'"
        
        # Convert to natural language description
        descriptions = database_service.convert_patients_to_natural_language([matching_patient])
        
        if descriptions:
            response = f"👤 **Patient Details for ID: {identification_number}**\n\n"
            response += descriptions[0]
            
            # Add additional details if available
            from datetime import datetime
            if matching_patient.get('birth_date'):
                try:
                    birth_date = matching_patient['birth_date']
                    if isinstance(birth_date, str):
                        birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
                    
                    today = datetime.now().date()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    response += f"\n\n📋 **Additional Information:**\n"
                    response += f"  • Current Age: {age} years\n"
                    response += f"  • Full Name: {matching_patient.get('full_name', 'N/A')}\n"
                    response += f"  • Email: {matching_patient.get('email', 'N/A')}\n"
                    response += f"  • Phone: {matching_patient.get('phone', 'N/A')}\n"
                except:
                    pass
            
            return response
        else:
            return f"❌ Error processing patient information for ID '{identification_number}'"
        
    except Exception as e:
        logger.error(f"Error getting patient by ID: {e}")
        return f"❌ Error retrieving patient information: {str(e)}"

@tool
def get_patients_summary() -> str:
    """
    Get a summary of all patients in the database.
    
    Returns only the total count of patients, without individual patient details.
    For detailed patient information, use search tools with specific criteria.
    
    **Requires Permission:** ViewPatients
    """
    try:
        # Check ViewPatients permission
        has_permission, error_msg = check_view_patients_permission()
        if not has_permission:
            return error_msg
        
        patients = database_service.get_all_patients()
        
        if not patients:
            return "📊 No patients found in the database"
        
        # Calculate basic statistics from real data
        total_patients = len(patients)
        patients_with_email = sum(1 for p in patients if p.get('email'))
        patients_with_phone = sum(1 for p in patients if p.get('phone'))
        patients_with_id = sum(1 for p in patients if p.get('identification_number'))
        
        # Calculate age distribution from birth dates
        from datetime import datetime
        ages = []
        for patient in patients:
            if patient.get('birth_date'):
                try:
                    birth_date = patient['birth_date']
                    if isinstance(birth_date, str):
                        birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
                    
                    today = datetime.now().date()
                    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    ages.append(age)
                except:
                    continue
        
        avg_age = sum(ages) / len(ages) if ages else 0
        min_age = min(ages) if ages else 0
        max_age = max(ages) if ages else 0
        
        response = f"📊 **Database Summary**\n\n"
        response += f"**Total Patients:** {total_patients}\n"
        response += f"**Contact Information:**\n"
        response += f"  • With Email: {patients_with_email}\n"
        response += f"  • With Phone: {patients_with_phone}\n"
        response += f"  • With ID Number: {patients_with_id}\n\n"
        
        if ages:
            response += f"**Age Statistics:**\n"
            response += f"  • Average Age: {avg_age:.1f} years\n"
            response += f"  • Age Range: {min_age} - {max_age} years\n"
            response += f"  • Patients with birth date: {len(ages)}\n\n"
        
        # NO incluir detalles de pacientes individuales por defecto
        response += f"💡 **Nota:** Para obtener información detallada de pacientes específicos, proporcione un número de identificación (IdentificationNumber) o use las herramientas de búsqueda específicas."
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting patients summary: {e}")
        return f"❌ Error getting patients summary: {str(e)}"

@tool  
def search_patients_by_name(name: str) -> str:
    """
    Search for patients by name (partial matches allowed).
    
    Args:
        name: Patient name to search for
        
    **Requires Permission:** ViewPatients
    """
    try:
        # Check ViewPatients permission
        has_permission, error_msg = check_view_patients_permission()
        if not has_permission:
            return error_msg
        
        # Use the database service's search function
        matching_patients = database_service.search_patients_by_name(name)
        
        if not matching_patients:
            return f"🔍 No patients found with name containing '{name}'"
        
        # Convert to natural language descriptions
        descriptions = database_service.convert_patients_to_natural_language(matching_patients)
        
        response = f"🔍 Found {len(matching_patients)} patient(s) with name containing '{name}':\n\n"
        
        for i, description in enumerate(descriptions, 1):
            response += f"{i}. {description}\n\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error searching patients by name: {e}")
        return f"❌ Error searching patients: {str(e)}"

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
        
    **Requires Permission:** ViewPatients
    """
    try:
        # Check ViewPatients permission
        has_permission, error_msg = check_view_patients_permission()
        if not has_permission:
            return error_msg
        
        patients = database_service.get_all_patients()
        
        if not patients:
            return "📊 No patients found in the database"
        
        filtered_patients = patients.copy()
        
        # Calculate ages from birth dates for filtering
        from datetime import datetime
        
        # Age filtering
        if age_min is not None or age_max is not None:
            age_filtered = []
            for patient in filtered_patients:
                if patient.get('birth_date'):
                    try:
                        birth_date = patient['birth_date']
                        if isinstance(birth_date, str):
                            birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
                        
                        today = datetime.now().date()
                        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                        
                        if age_min is not None and age < age_min:
                            continue
                        if age_max is not None and age > age_max:
                            continue
                        
                        age_filtered.append(patient)
                    except:
                        continue
            filtered_patients = age_filtered
        
        # Email domain filtering with normalization
        if email_domain:
            normalized_domain = normalize_text_for_search(email_domain)
            filtered_patients = [
                p for p in filtered_patients 
                if normalize_text_for_search(p.get('email', '')).endswith(normalized_domain)
            ]
        
        # Year of birth filtering
        if year_of_birth:
            birth_year_filtered = []
            for patient in filtered_patients:
                if patient.get('birth_date'):
                    try:
                        birth_date = patient['birth_date']
                        if isinstance(birth_date, str):
                            birth_year = int(birth_date.split('-')[0])
                        else:
                            birth_year = birth_date.year
                        
                        if birth_year == year_of_birth:
                            birth_year_filtered.append(patient)
                    except:
                        continue
            filtered_patients = birth_year_filtered
        
        if not filtered_patients:
            return f"🔍 No patients found matching the specified criteria"
        
        # Build filter description
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
        
        # Convert to natural language descriptions
        descriptions = database_service.convert_patients_to_natural_language(filtered_patients)
        
        response = f"🔍 Found {len(filtered_patients)} patient(s) matching criteria: {filter_desc}\n\n"
        
        for i, description in enumerate(descriptions, 1):
            response += f"{i}. {description}\n\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error filtering patients: {e}")
        return f"❌ Error filtering patients: {str(e)}"
        
        return response
        
    except Exception as e:
        logger.error(f"Error filtering patients: {e}")
        return f"❌ Error filtering patients: {str(e)}"

@tool
def search_patients_by_condition(contact_info: str) -> str:
    """
    Search for patients by contact information (phone or email).
    Since medical conditions are not available in the current database,
    this tool searches by contact information instead.
    
    Args:
        contact_info: Phone number or email to search for (partial matches allowed)
        
    **Requires Permission:** ViewPatients
    """
    try:
        # Check ViewPatients permission
        has_permission, error_msg = check_view_patients_permission()
        if not has_permission:
            return error_msg
        
        patients = database_service.get_all_patients()
        
        if not patients:
            return "📊 No patients found in the database"
        
        # Filter by phone or email with normalization for better matching
        normalized_contact = normalize_text_for_search(contact_info)
        matching_patients = []
        
        for patient in patients:
            phone = normalize_text_for_search(patient.get('phone', ''))
            email = normalize_text_for_search(patient.get('email', ''))
            
            if normalized_contact in phone or normalized_contact in email:
                matching_patients.append(patient)
        
        if not matching_patients:
            return f"🔍 No patients found with contact info containing '{contact_info}'"
        
        # Convert to natural language descriptions
        descriptions = database_service.convert_patients_to_natural_language(matching_patients)
        
        response = f"🔍 Found {len(matching_patients)} patient(s) with contact info containing '{contact_info}':\n\n"
        
        for i, description in enumerate(descriptions, 1):
            response += f"{i}. {description}\n\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error searching patients by contact info: {e}")
        return f"❌ Error searching patients by contact info: {str(e)}"

def check_create_patients_permission() -> tuple[bool, str]:
    """
    Check if the current user has ManagePatients permission.
    
    Returns:
        tuple: (has_permission, error_message_if_not)
    """
    if not permission_context.has_permission("ManagePatients"):
        username = permission_context.get_username() or "Unknown"
        permissions = permission_context.get_permissions()
        
        error_msg = f"""🚫 **Acceso Denegado**

El usuario '{username}' no tiene permisos para crear nuevos pacientes.

**Permisos actuales:** {', '.join(permissions) if permissions else 'Ninguno'}
**Permiso requerido:** ManagePatients

Por favor, contacte al administrador del sistema para obtener los permisos necesarios."""
        
        return False, error_msg
    
    return True, ""

@tool
def create_patient(
    name: str,
    identification_number: str,
    date_of_birth: str,
    age: int,
    phone_number: str,
    email: str
) -> str:
    """
    Create a new patient in the external backend system.
    
    Args:
        name: Full name of the patient
        identification_number: Patient's identification number (must be unique)
        date_of_birth: Date of birth in ISO format (YYYY-MM-DDTHH:mm:ss.sssZ)
        age: Age of the patient in years
        phone_number: Patient's phone number
        email: Patient's email address
    
    Examples:
    - create_patient("Juan Pérez", "12345678", "1990-05-15T00:00:00.000Z", 33, "+57-300-123-4567", "juan.perez@email.com")
    - create_patient("María García", "87654321", "1985-12-10T00:00:00.000Z", 38, "+57-301-987-6543", "maria.garcia@gmail.com")
    
    **Requires Permission:** ManagePatients
    """
    try:
        # Check ManagePatients permission
        has_permission, error_msg = check_create_patients_permission()
        if not has_permission:
            return error_msg
        
        # Get JWT token from permission context
        jwt_token = permission_context.get_jwt_token()
        if not jwt_token:
            return "❌ Error: No se encontró el token JWT para autenticación con el backend externo"
        
        # Prepare the payload
        payload = {
            "patientId": "0",  # Auto-generated by the backend
            "name": name,
            "identificationNumber": identification_number,
            "dateOfBirth": date_of_birth,
            "age": age,
            "phoneNumber": phone_number,
            "email": email
        }
        
        # Make HTTP request to external backend
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        
        url = f"{settings.EXTERNAL_BACKEND_API_URL.rstrip('/')}/Patient/create"
        
        # Log the request for debugging
        logger.info(f"Making request to: {url}")
        logger.info(f"Request payload: {payload}")
        logger.info(f"Request headers: {{'Content-Type': 'application/json', 'Authorization': 'Bearer [TOKEN]'}}")
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                url=url,
                json=payload,
                headers=headers
            )
            
            # Log the response for debugging
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            logger.info(f"Response text: {response.text}")
            
            if response.status_code == 200 or response.status_code == 201:
                # Success
                try:
                    result = response.json()
                    patient_id = result.get('patientId', 'N/A')
                    
                    success_msg = f"""✅ **Paciente Creado Exitosamente**

**Información del paciente:**
  • ID del Sistema: {patient_id}
  • Nombre: {name}
  • Número de Identificación: {identification_number}
  • Fecha de Nacimiento: {date_of_birth}
  • Edad: {age} años
  • Teléfono: {phone_number}
  • Email: {email}

El paciente ha sido registrado correctamente en el sistema."""
                    
                    return success_msg
                    
                except json.JSONDecodeError:
                    return f"""✅ **Paciente Creado Exitosamente**

El paciente '{name}' con identificación '{identification_number}' ha sido registrado correctamente en el sistema.
Código de respuesta: {response.status_code}"""
                    
            elif response.status_code == 400:
                # Bad request - validation errors
                try:
                    error_data = response.json()
                    error_details = error_data.get('errors', error_data.get('message', 'Error de validación'))
                    
                    return f"""❌ **Error de Validación**

No se pudo crear el paciente debido a errores en los datos proporcionados:

**Detalles del error:** {error_details}

Por favor, verifique que:
  • El número de identificación no esté duplicado
  • El formato de fecha sea correcto (YYYY-MM-DDTHH:mm:ss.sssZ)
  • El email tenga un formato válido
  • Todos los campos requeridos estén completos"""
                    
                except json.JSONDecodeError:
                    return f"❌ Error de validación: {response.text}"
                    
            elif response.status_code == 401:
                return "❌ Error de autenticación: Token JWT inválido o expirado"
                
            elif response.status_code == 403:
                return "❌ Error de autorización: No tiene permisos para crear pacientes en el backend externo"
                
            else:
                # Other errors
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', f'Error del servidor: {response.status_code}')
                except json.JSONDecodeError:
                    error_msg = f'Error del servidor: {response.status_code} - {response.text}'
                
                return f"❌ Error al crear el paciente: {error_msg}"
        
    except httpx.TimeoutException:
        return "❌ Error: Tiempo de espera agotado al contactar el backend externo"
        
    except httpx.RequestError as e:
        return f"❌ Error de conexión al backend externo: {str(e)}"
        
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        return f"❌ Error inesperado al crear el paciente: {str(e)}"

@tool
def update_patient(
    identification_number: str,
    name: Optional[str] = None,
    date_of_birth: Optional[str] = None,
    age: Optional[int] = None,
    phone_number: Optional[str] = None,
    email: Optional[str] = None
) -> str:
    """
    Update patient information in the external backend system.
    The identification_number is required, and you can update any combination of the other fields.
    
    Args:
        identification_number: Patient's identification number (required for lookup)
        name: New full name of the patient (optional)
        date_of_birth: New date of birth in ISO format (YYYY-MM-DDTHH:mm:ss.sssZ) (optional)
        age: New age of the patient in years (optional)
        phone_number: New phone number (optional)
        email: New email address (optional)
    
    Examples:
    - update_patient("12345678", name="Juan Carlos Pérez")
    - update_patient("87654321", email="nueva.email@gmail.com", phone_number="+57-301-555-1234")
    - update_patient("11223344", age=31, date_of_birth="1992-08-15T00:00:00.000Z")
    
    **Requires Permission:** ManagePatients
    """
    try:
        # Check ManagePatients permission
        has_permission, error_msg = check_create_patients_permission()
        if not has_permission:
            return error_msg
        
        # Get JWT token from permission context
        jwt_token = permission_context.get_jwt_token()
        if not jwt_token:
            return "❌ Error: No se encontró el token JWT para autenticación con el backend externo"
        
        # Get the raw patient data from database directly
        patients = database_service.get_all_patients()
        current_patient = None
        for patient in patients:
            if patient.get('identification_number') == identification_number:
                current_patient = patient
                break
        
        if not current_patient:
            return f"❌ Error: No se pudo encontrar el paciente con identificación '{identification_number}'"
        
        # Log current patient data for debugging
        logger.info(f"Current patient data: {current_patient}")
        
        # Extract and prepare current data with proper defaults
        current_name = current_patient.get('full_name') or current_patient.get('name', '')
        current_phone = current_patient.get('phone') or current_patient.get('phone_number', '')
        current_email = current_patient.get('email', '')
        current_age = current_patient.get('age', 0)
        
        # Handle birth_date formatting
        current_birth_date = current_patient.get('birth_date', '')
        if current_birth_date:
            # Ensure ISO format with timezone
            if isinstance(current_birth_date, str):
                if 'T' not in current_birth_date:
                    current_birth_date = current_birth_date + 'T00:00:00'
                if not current_birth_date.endswith('Z') and not current_birth_date.endswith('.000Z'):
                    if '.' not in current_birth_date:
                        current_birth_date = current_birth_date + '.000Z'
                    else:
                        current_birth_date = current_birth_date + 'Z'
        else:
            current_birth_date = '1900-01-01T00:00:00.000Z'  # Default if missing
        
        # Build the COMPLETE payload - always send ALL fields
        payload = {
            "patientId": "0",  # Always "0" as specified
            "name": str(name if name is not None else current_name),
            "identificationNumber": str(identification_number),
            "dateOfBirth": str(date_of_birth if date_of_birth is not None else current_birth_date),
            "age": int(age if age is not None else current_age),
            "phoneNumber": str(phone_number if phone_number is not None else current_phone),
            "email": str(email if email is not None else current_email)
        }
        
        # Log the complete payload for debugging
        logger.info(f"Complete payload being sent: {payload}")
        
        # Make HTTP request to external backend
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        
        url = f"{settings.EXTERNAL_BACKEND_API_URL.rstrip('/')}/Patient/update-patient"
        
        # Log the request for debugging
        logger.info(f"Making PUT request to: {url}")
        logger.info(f"Request payload: {payload}")
        logger.info(f"Request headers: {{'Content-Type': 'application/json', 'Authorization': 'Bearer [TOKEN]'}}")
        
        with httpx.Client(timeout=30.0) as client:
            response = client.put(
                url=url,
                json=payload,
                headers=headers
            )
            
            # Log the response for debugging
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            logger.info(f"Response text: {response.text}")
            
            if response.status_code == 200 or response.status_code == 204:
                # Success
                updated_fields = []
                if name is not None:
                    updated_fields.append(f"Nombre: {name}")
                if date_of_birth is not None:
                    updated_fields.append(f"Fecha de Nacimiento: {date_of_birth}")
                if age is not None:
                    updated_fields.append(f"Edad: {age} años")
                if phone_number is not None:
                    updated_fields.append(f"Teléfono: {phone_number}")
                if email is not None:
                    updated_fields.append(f"Email: {email}")
                
                success_msg = f"""✅ **Paciente Actualizado Exitosamente**

**Paciente:** {identification_number}
**Campos actualizados:**
{chr(10).join(f"  • {field}" for field in updated_fields)}

La información del paciente ha sido actualizada correctamente en el sistema."""
                
                return success_msg
                    
            elif response.status_code == 400:
                # Bad request - validation errors
                try:
                    error_data = response.json()
                    error_details = error_data.get('errors', error_data.get('message', 'Error de validación'))
                    
                    return f"""❌ **Error de Validación**

No se pudo actualizar el paciente debido a errores en los datos proporcionados:

**Detalles del error:** {error_details}

Por favor, verifique que:
  • El número de identificación sea válido
  • El formato de fecha sea correcto (YYYY-MM-DDTHH:mm:ss.sssZ)
  • El email tenga un formato válido
  • Los campos proporcionados sean válidos"""
                    
                except json.JSONDecodeError:
                    return f"❌ Error de validación: {response.text}"
                    
            elif response.status_code == 401:
                return "❌ Error de autenticación: Token JWT inválido o expirado"
                
            elif response.status_code == 403:
                return "❌ Error de autorización: No tiene permisos para actualizar pacientes en el backend externo"
                
            elif response.status_code == 404:
                return f"❌ Error: El paciente con identificación '{identification_number}' no fue encontrado en el backend externo"
                
            else:
                # Other errors
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', f'Error del servidor: {response.status_code}')
                except json.JSONDecodeError:
                    error_msg = f'Error del servidor: {response.status_code} - {response.text}'
                
                return f"❌ Error al actualizar el paciente: {error_msg}"
        
    except httpx.TimeoutException:
        return "❌ Error: Tiempo de espera agotado al contactar el backend externo"
        
    except httpx.RequestError as e:
        return f"❌ Error de conexión al backend externo: {str(e)}"
        
    except Exception as e:
        logger.error(f"Error updating patient: {e}")
        return f"❌ Error inesperado al actualizar el paciente: {str(e)}"

# List of all available tools for the agent
ALL_TOOLS = [
    search_patients,
    get_patients_summary,
    search_patients_by_name,
    filter_patients_by_demographics,
    search_patients_by_condition,
    get_patient_by_id,
    create_patient,
    update_patient
]
