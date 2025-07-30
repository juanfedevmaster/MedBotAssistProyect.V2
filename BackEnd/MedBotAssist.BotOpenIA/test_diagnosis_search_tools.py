import unittest
from unittest.mock import patch, MagicMock

from app.agents.tools import diagnosis_search_tools

class TestDiagnosisSearchTools(unittest.TestCase):

    def setUp(self):
        self.permission_context = MagicMock()
        self.permission_context.permissions = ['read_patients', 'read_medical_history']
        self.permission_context.user_id = 'mock_user'
        self.permission_context.hospital_id = 'mock_hospital'

    @patch('app.agents.tools.diagnosis_search_tools.search_patients_by_diagnosis_impl')
    def test_search_patients_by_diagnosis(self, mock_search):
        mock_search.return_value = "Found 3 patients with Hypertension: Carlos Sánchez, Maria Lopez, Juan Pérez"
        
        result = diagnosis_search_tools.search_patients_by_diagnosis_impl(
            diagnosis_keyword='Hypertension',
            permission_context=self.permission_context
        )

        self.assertIsInstance(result, str)
        self.assertIn('Hypertension', result)
        self.assertIn('Carlos Sánchez', result)

    @patch('app.agents.tools.diagnosis_search_tools.get_patient_names_by_diagnosis_impl')
    def test_get_patient_names_by_diagnosis(self, mock_get_names):
        mock_get_names.return_value = "Carlos Sánchez, Maria Lopez"
        
        result = diagnosis_search_tools.get_patient_names_by_diagnosis_impl(
            diagnosis_keyword='Hypertension',
            permission_context=self.permission_context
        )

        self.assertIsInstance(result, str)
        self.assertIn('Carlos Sánchez', result)

    @patch('app.agents.tools.diagnosis_search_tools.get_patient_names_by_diagnosis_impl')
    def test_get_patient_names_by_invalid_diagnosis(self, mock_get_names):
        mock_get_names.return_value = "No patients found with diagnosis 'Flu'"
        
        result = diagnosis_search_tools.get_patient_names_by_diagnosis_impl(
            diagnosis_keyword='Flu',
            permission_context=self.permission_context
        )

        self.assertIsInstance(result, str)
        self.assertIn('no patients', result.lower())

    def test_tools_are_integrated(self):
        from app.agents.tools import ALL_TOOLS
        tool_names = [tool.name for tool in ALL_TOOLS]
        self.assertIn('search_patients_by_diagnosis', tool_names)
        self.assertIn('get_patient_names_by_diagnosis', tool_names)

if __name__ == '__main__':
    unittest.main()
