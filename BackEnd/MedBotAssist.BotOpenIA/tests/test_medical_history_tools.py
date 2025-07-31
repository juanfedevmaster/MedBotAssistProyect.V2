import unittest
from unittest.mock import AsyncMock, MagicMock

class TestMedicalHistoryTools(unittest.IsolatedAsyncioTestCase):
    
    async def asyncSetUp(self):
        self.mock_get_medical_history = MagicMock()
        self.mock_get_diagnoses_summary = MagicMock()
        self.mock_count_by_diagnosis = MagicMock()

        self.mock_get_medical_history.invoke = AsyncMock(return_value="Carlos Sánchez tiene antecedentes de hipertensión y diabetes.")
        self.mock_get_diagnoses_summary.invoke = AsyncMock(return_value="Carlos Sánchez ha sido diagnosticado con hipertensión en 2022.")
        self.mock_count_by_diagnosis.invoke = AsyncMock(return_value="Se encontraron 12 pacientes con diagnóstico de hipertensión.")

    async def test_get_medical_history_valid_id(self):
        result = await self.mock_get_medical_history.invoke({"identification_number": "ID001"})
        self.assertIn("hipertensión", result.lower())
        self.assertIn("diabetes", result.lower())

    async def test_get_diagnoses_summary_valid_id(self):
        result = await self.mock_get_diagnoses_summary.invoke({"identification_number": "ID001"})
        self.assertIn("diagnosticado", result.lower())
        self.assertIn("hipertensión", result.lower())

    async def test_get_medical_history_invalid_id(self):
        self.mock_get_medical_history.invoke = AsyncMock(return_value="No patient found with identification number 'NONEXISTENT'.")
        result = await self.mock_get_medical_history.invoke({"identification_number": "NONEXISTENT"})
        self.assertIn("no patient found", result.lower())

    async def test_count_patients_by_diagnosis_hypertension(self):
        result = await self.mock_count_by_diagnosis.invoke({"diagnosis_keyword": "Hipertensión"})
        self.assertIn("hipertensión", result.lower())
        self.assertIn("12", result)

    async def test_count_patients_by_diagnosis_diabetes(self):
        self.mock_count_by_diagnosis.invoke = AsyncMock(return_value="Se encontraron 7 pacientes con diagnóstico de diabetes.")
        result = await self.mock_count_by_diagnosis.invoke({"diagnosis_keyword": "diabetes"})
        self.assertIn("diabetes", result.lower())
        self.assertIn("7", result)

if __name__ == "__main__":
    unittest.main()
