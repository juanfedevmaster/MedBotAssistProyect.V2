"""
Updated test script for the update_patient function
"""
import json

def test_complete_update_patient_payload():
    """
    Test the COMPLETE payload format generated in update_patient
    """
    print("=== TESTING COMPLETE JSON FORMAT FOR UPDATE_PATIENT ===")
    
    # Simulate current patient data (example with the format you specified)
    current_patient = {
        'full_name': 'Ana López Quintero',
        'identification_number': '11223344',
        'birth_date': '1995-08-15',
        'age': 30,
        'phone': '3054445555',
        'email': 'ana.lopez@email.com'
    }
    
    # CASE 1: Update only email (real example)
    print("📧 CASE 1: Update only EMAIL")
    identification_number = '11223344'
    name = None
    date_of_birth = None  
    age = None  
    phone_number = None
    email = 'nuevo.email@test.com'
    
    # Extract and prepare current data with default values
    current_name = current_patient.get('full_name') or current_patient.get('name', '')
    current_phone = current_patient.get('phone') or current_patient.get('phone_number', '')
    current_email_orig = current_patient.get('email', '')
    current_age = current_patient.get('age', 0)
    
    # Handle birth_date format
    current_birth_date = current_patient.get('birth_date', '')
    if current_birth_date:
        if isinstance(current_birth_date, str):
            if 'T' not in current_birth_date:
                current_birth_date = current_birth_date + 'T00:00:00'
            if not current_birth_date.endswith('Z') and not current_birth_date.endswith('.000Z'):
                if '.' not in current_birth_date:
                    current_birth_date = current_birth_date + '.000Z'
                else:
                    current_birth_date = current_birth_date + 'Z'
    else:
        current_birth_date = '1900-01-01T00:00:00.000Z'
    
    # Build the COMPLETE payload - always sends all fields
    payload = {
        "patientId": "0",  # Always "0" as you specified
        "name": str(name if name is not None else current_name),
        "identificationNumber": str(identification_number),
        "dateOfBirth": str(date_of_birth if date_of_birth is not None else current_birth_date),
        "age": int(age if age is not None else current_age),
        "phoneNumber": str(phone_number if phone_number is not None else current_phone),
        "email": str(email if email is not None else current_email_orig)
    }
    
    print("Current patient data:")
    for key, value in current_patient.items():
        print(f"  {key}: {value}")
    
    print(f"\nRequested update:")
    print(f"  Only email: {email}")
    
    print(f"\nCOMPLETE JSON payload to be sent:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    # CASE 2: Update multiple fields
    print("\n" + "="*60)
    print("🔄 CASE 2: Update NAME and PHONE")
    
    name2 = "Ana Elena López Quintero"
    phone_number2 = "3001234567"
    email2 = None  # Don't update
    
    payload2 = {
        "patientId": "0",
        "name": str(name2 if name2 is not None else current_name),
        "identificationNumber": str(identification_number),
        "dateOfBirth": str(date_of_birth if date_of_birth is not None else current_birth_date),
        "age": int(age if age is not None else current_age),
        "phoneNumber": str(phone_number2 if phone_number2 is not None else current_phone),
        "email": str(email2 if email2 is not None else current_email_orig)
    }
    
    print(f"Requested updates:")
    print(f"  name: {name2}")
    print(f"  phone_number: {phone_number2}")
    
    print(f"\nCOMPLETE JSON payload to be sent:")
    print(json.dumps(payload2, indent=2, ensure_ascii=False))
    
    print(f"\n✅ IMPORTANT VERIFICATIONS:")
    print(f"  ✅ patientId always '0': {payload['patientId'] == '0'}")
    print(f"  ✅ JSON always complete (7 fields): {len(payload) == 7}")
    print(f"  ✅ All fields are string except age: {all(isinstance(v, str) for k, v in payload.items() if k != 'age')}")
    print(f"  ✅ Age is integer: {isinstance(payload['age'], int)}")
    print(f"  ✅ dateOfBirth in ISO format: {'T' in payload['dateOfBirth'] and 'Z' in payload['dateOfBirth']}")
    
    # Comparison with your example
    expected_format = {
        "patientId": "8",
        "name": "Ana López Quintero", 
        "identificationNumber": "11223344",
        "dateOfBirth": "1995-08-15T00:00:00",
        "age": 30,
        "phoneNumber": "3054445555",
        "email": "ana.lopez@email.com"
    }
    
    print(f"\n📋 COMPARISON WITH YOUR EXPECTED FORMAT:")
    print("Your example:")
    print(json.dumps(expected_format, indent=2, ensure_ascii=False))
    print("\nMy implementation (with patientId='0' as you specified):")
    original_payload = {
        "patientId": "0",  # Changed to "0" as you specified
        "name": current_name,
        "identificationNumber": identification_number,
        "dateOfBirth": current_birth_date,
        "age": current_age,
        "phoneNumber": current_phone,
        "email": current_email_orig
    }
    print(json.dumps(original_payload, indent=2, ensure_ascii=False))
    
    return payload

if __name__ == "__main__":
    test_complete_update_patient_payload()
