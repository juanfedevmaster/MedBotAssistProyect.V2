"""
Medical Agent Tools Package

This package contains all the tools used by the medical agent, organized by functionality.
"""

from .patient_search_tools import (
    search_patients,
    search_patients_by_name,
    search_patients_by_condition,
    get_patient_by_id,
    get_patients_summary,
    filter_patients_by_demographics
)

from .patient_management_tools import (
    create_patient,
    update_patient
)

from .medical_history_tools import (
    get_patient_medical_history,
    get_patient_diagnoses_summary,
    count_patients_by_diagnosis
)

from .diagnosis_search_tools import (
    search_patients_by_diagnosis,
    get_patient_names_by_diagnosis
)

from .instructive_search_tools import (
    search_instructive_info,
    get_available_instructives_list
)

from .permission_validators import (
    check_use_agent_permission,
    check_view_patients_permission,
    check_create_patients_permission
)

# Export all tools for the agent
ALL_TOOLS = [
    # Search and query tools
    search_patients,
    get_patients_summary,
    search_patients_by_name,
    filter_patients_by_demographics,
    search_patients_by_condition,
    get_patient_by_id,
    
    # Medical history tools
    get_patient_medical_history,
    get_patient_diagnoses_summary,
    count_patients_by_diagnosis,
    
    # Diagnosis search tools
    search_patients_by_diagnosis,
    get_patient_names_by_diagnosis,
    
    # Instructive search tools
    search_instructive_info,
    get_available_instructives_list,
    
    # Management tools
    create_patient,
    update_patient
]

__all__ = [
    'ALL_TOOLS',
    'search_patients',
    'search_patients_by_name', 
    'search_patients_by_condition',
    'get_patient_by_id',
    'get_patients_summary',
    'filter_patients_by_demographics',
    'get_patient_medical_history',
    'get_patient_diagnoses_summary',
    'count_patients_by_diagnosis',
    'search_patients_by_diagnosis',
    'get_patient_names_by_diagnosis',
    'search_instructive_info',
    'get_available_instructives_list',
    'create_patient',
    'update_patient',
    'check_use_agent_permission',
    'check_view_patients_permission',
    'check_create_patients_permission'
]
