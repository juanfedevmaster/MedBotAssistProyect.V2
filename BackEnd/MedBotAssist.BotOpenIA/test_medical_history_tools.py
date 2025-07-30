#!/usr/bin/env python3
"""
Test script for medical history tools
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.tools.medical_history_tools import get_patient_medical_history, get_patient_diagnoses_summary, count_patients_by_diagnosis

def test_medical_history_tools():
    """Test the new medical history tools"""
    
    print("🔬 Testing Medical History Tools")
    print("=" * 50)
    
    # Test with a known patient ID from the database
    test_id = "ID001"  # Carlos Sánchez
    
    print(f"\n📋 Testing get_patient_medical_history with ID: {test_id}")
    print("-" * 50)
    
    try:
        result = get_patient_medical_history.invoke({"identification_number": test_id})
        print(f"✅ Result: {result[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n🩺 Testing get_patient_diagnoses_summary with ID: {test_id}")
    print("-" * 50)
    
    try:
        result = get_patient_diagnoses_summary.invoke({"identification_number": test_id})
        print(f"✅ Result: {result[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n🔍 Testing with non-existent ID")
    print("-" * 50)
    
    try:
        result = get_patient_medical_history.invoke({"identification_number": "NONEXISTENT"})
        print(f"✅ Result: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n📊 Testing count_patients_by_diagnosis with keyword: 'Hypertension'")
    print("-" * 50)
    
    try:
        result = count_patients_by_diagnosis.invoke({"diagnosis_keyword": "Hipertensión"})
        print(f"✅ Result: {result[:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n📊 Testing count_patients_by_diagnosis with keyword: 'diabetes'")
    print("-" * 50)
    
    try:
        result = count_patients_by_diagnosis.invoke({"diagnosis_keyword": "diabetes"})
        print(f"✅ Result: {result[:300]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_medical_history_tools()
