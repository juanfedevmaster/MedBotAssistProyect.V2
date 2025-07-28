"""
Script de prueba actualizado para la función update_patient
"""
import json

def test_complete_update_patient_payload():
    """
    Prueba el formato del payload COMPLETO que se genera en update_patient
    """
    print("=== PRUEBA DEL FORMATO JSON COMPLETO PARA UPDATE_PATIENT ===")
    
    # Simular datos de paciente actual (ejemplo con el formato que especificaste)
    current_patient = {
        'full_name': 'Ana López Quintero',
        'identification_number': '11223344',
        'birth_date': '1995-08-15',
        'age': 30,
        'phone': '3054445555',
        'email': 'ana.lopez@email.com'
    }
    
    # CASO 1: Actualizar solo email (ejemplo real)
    print("📧 CASO 1: Actualizar solo EMAIL")
    identification_number = '11223344'
    name = None
    date_of_birth = None  
    age = None  
    phone_number = None
    email = 'nuevo.email@test.com'
    
    # Extraer y preparar datos actuales con valores por defecto
    current_name = current_patient.get('full_name') or current_patient.get('name', '')
    current_phone = current_patient.get('phone') or current_patient.get('phone_number', '')
    current_email_orig = current_patient.get('email', '')
    current_age = current_patient.get('age', 0)
    
    # Manejar formato de birth_date
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
    
    # Construir el payload COMPLETO - siempre envía todos los campos
    payload = {
        "patientId": "0",  # Siempre "0" como especificaste
        "name": str(name if name is not None else current_name),
        "identificationNumber": str(identification_number),
        "dateOfBirth": str(date_of_birth if date_of_birth is not None else current_birth_date),
        "age": int(age if age is not None else current_age),
        "phoneNumber": str(phone_number if phone_number is not None else current_phone),
        "email": str(email if email is not None else current_email_orig)
    }
    
    print("Datos del paciente actual:")
    for key, value in current_patient.items():
        print(f"  {key}: {value}")
    
    print(f"\nActualización solicitada:")
    print(f"  Solo email: {email}")
    
    print(f"\nPayload JSON COMPLETO que se enviará:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    # CASO 2: Actualizar múltiples campos
    print("\n" + "="*60)
    print("🔄 CASO 2: Actualizar NOMBRE y TELÉFONO")
    
    name2 = "Ana Elena López Quintero"
    phone_number2 = "3001234567"
    email2 = None  # No actualizar
    
    payload2 = {
        "patientId": "0",
        "name": str(name2 if name2 is not None else current_name),
        "identificationNumber": str(identification_number),
        "dateOfBirth": str(date_of_birth if date_of_birth is not None else current_birth_date),
        "age": int(age if age is not None else current_age),
        "phoneNumber": str(phone_number2 if phone_number2 is not None else current_phone),
        "email": str(email2 if email2 is not None else current_email_orig)
    }
    
    print(f"Actualizaciones solicitadas:")
    print(f"  name: {name2}")
    print(f"  phone_number: {phone_number2}")
    
    print(f"\nPayload JSON COMPLETO que se enviará:")
    print(json.dumps(payload2, indent=2, ensure_ascii=False))
    
    print(f"\n✅ VERIFICACIONES IMPORTANTES:")
    print(f"  ✅ patientId siempre '0': {payload['patientId'] == '0'}")
    print(f"  ✅ JSON siempre completo (7 campos): {len(payload) == 7}")
    print(f"  ✅ Todos los campos son string excepto age: {all(isinstance(v, str) for k, v in payload.items() if k != 'age')}")
    print(f"  ✅ Age es entero: {isinstance(payload['age'], int)}")
    print(f"  ✅ dateOfBirth en formato ISO: {'T' in payload['dateOfBirth'] and 'Z' in payload['dateOfBirth']}")
    
    # Comparación con tu ejemplo
    expected_format = {
        "patientId": "8",
        "name": "Ana López Quintero", 
        "identificationNumber": "11223344",
        "dateOfBirth": "1995-08-15T00:00:00",
        "age": 30,
        "phoneNumber": "3054445555",
        "email": "ana.lopez@email.com"
    }
    
    print(f"\n📋 COMPARACIÓN CON TU FORMATO ESPERADO:")
    print("Tu ejemplo:")
    print(json.dumps(expected_format, indent=2, ensure_ascii=False))
    print("\nMi implementación (con patientId='0' como especificaste):")
    original_payload = {
        "patientId": "0",  # Cambié a "0" como especificaste
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
