# test_complete_update.py
import pytest
from datetime import datetime

def build_payload(current_patient, updates):
    """
    Helper to build the COMPLETE payload, applying updates over current_patient.
    """
    # Extract and normalize current values
    current_name = current_patient.get('full_name') or current_patient.get('name', '')
    current_phone = current_patient.get('phone') or current_patient.get('phone_number', '')
    current_email = current_patient.get('email', '')
    current_age = current_patient.get('age', 0)

    birth_date = current_patient.get('birth_date', '')
    if birth_date:
        if isinstance(birth_date, str):
            if 'T' not in birth_date:
                birth_date += 'T00:00:00'
            if not birth_date.endswith('Z') and not birth_date.endswith('.000Z'):
                if '.' not in birth_date:
                    birth_date += '.000Z'
                else:
                    birth_date += 'Z'
    else:
        birth_date = '1900-01-01T00:00:00.000Z'

    return {
        "patientId": "0",
        "name": str(updates.get('name', current_name)),
        "identificationNumber": str(updates.get('identification_number', current_patient['identification_number'])),
        "dateOfBirth": str(updates.get('birth_date', birth_date)),
        "age": int(updates.get('age', current_age)),
        "phoneNumber": str(updates.get('phone_number', current_phone)),
        "email": str(updates.get('email', current_email))
    }

@pytest.fixture
def current_patient():
    return {
        'full_name': 'Ana López Quintero',
        'identification_number': '11223344',
        'birth_date': '1995-08-15',
        'age': 30,
        'phone': '3054445555',
        'email': 'ana.lopez@email.com'
    }

def test_update_only_email(current_patient):
    updates = {
        'email': 'nuevo.email@test.com'
    }
    payload = build_payload(current_patient, updates)
    
    assert payload['patientId'] == '0'
    assert payload['email'] == 'nuevo.email@test.com'
    assert payload['name'] == 'Ana López Quintero'
    assert payload['phoneNumber'] == '3054445555'
    assert isinstance(payload['age'], int)
    assert 'T' in payload['dateOfBirth'] and 'Z' in payload['dateOfBirth']
    assert len(payload) == 7

def test_update_name_and_phone(current_patient):
    updates = {
        'name': 'Ana Elena López Quintero',
        'phone_number': '3001234567'
    }
    payload = build_payload(current_patient, updates)

    assert payload['name'] == 'Ana Elena López Quintero'
    assert payload['phoneNumber'] == '3001234567'
    assert payload['email'] == 'ana.lopez@email.com'
    assert payload['identificationNumber'] == '11223344'
    assert isinstance(payload['age'], int)
    assert 'T' in payload['dateOfBirth'] and 'Z' in payload['dateOfBirth']
    assert len(payload) == 7
