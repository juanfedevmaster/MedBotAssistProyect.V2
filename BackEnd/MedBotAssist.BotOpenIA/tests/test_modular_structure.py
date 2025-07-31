# test_modular_structure.py

import unittest
from app.agents.tools import (
    ALL_TOOLS,
    search_patients,
    create_patient,
    check_use_agent_permission
)
from app.agents.tools.permission_validators import (
    check_use_agent_permission,
    check_view_patients_permission,
    check_create_patients_permission,
    validate_patient_view_permissions,
    validate_patient_management_permissions
)
from app.agents.tools.patient_search_tools import (
    search_patients,
    search_patients_by_name,
    get_patient_by_id,
    get_patients_summary
)
from app.agents.tools.patient_management_tools import (
    create_patient,
    update_patient
)
from app.agents.medical_agent import MedicalQueryAgent

class TestModularStructure(unittest.TestCase):

    def test_all_tools_are_imported(self):
        expected_tools = [
            'search_patients',
            'get_patients_summary', 
            'search_patients_by_name',
            'filter_patients_by_demographics',
            'search_patients_by_condition',
            'get_patient_by_id',
            'create_patient',
            'update_patient'
        ]
        tool_names = [tool.name for tool in ALL_TOOLS]
        for expected in expected_tools:
            self.assertIn(expected, tool_names, f"{expected} missing in ALL_TOOLS")

    def test_individual_module_imports(self):
        self.assertTrue(callable(check_use_agent_permission))
        self.assertTrue(callable(check_view_patients_permission))
        self.assertTrue(callable(search_patients))
        self.assertTrue(callable(create_patient))

    def test_specific_imports_from_package(self):
        self.assertTrue(callable(search_patients))
        self.assertTrue(callable(create_patient))
        self.assertTrue(callable(check_use_agent_permission))

    def test_tool_structure(self):
        for tool in ALL_TOOLS:
            self.assertTrue(hasattr(tool, "name"))
            self.assertTrue(hasattr(tool, "description"))
            self.assertIsInstance(tool.name, str)
            self.assertIsInstance(tool.description, str)

            # Only check for permission keywords if description mentions permissions
            if "permission" in tool.description.lower() or "requires" in tool.description.lower():
                self.assertTrue(
                    any(kw in tool.description for kw in ["UseAgent", "ViewPatients", "ManagePatients"]),
                    f"{tool.name} mentions permission but lacks specific keyword"
                )

    def test_medical_agent_tool_access(self):
        agent = MedicalQueryAgent()
        self.assertIsNotNone(agent.agent_executor)
        tools = agent.get_available_tools()
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        for tool_info in tools[:3]:
            self.assertIn("name", tool_info)

    def test_permission_validators_return_format(self):
        has_view, msg_view = validate_patient_view_permissions()
        has_manage, msg_manage = validate_patient_management_permissions()

        self.assertIsInstance(has_view, bool)
        self.assertIsInstance(msg_view, str)
        self.assertIn("UseAgent", msg_view)
        self.assertTrue(
            "ViewPatients" in msg_view or "access denied" in msg_view.lower() or "permission" in msg_view.lower(),
            f"Unexpected view permission message: {msg_view}"
        )

        self.assertIsInstance(has_manage, bool)
        self.assertIsInstance(msg_manage, str)
        self.assertIn("UseAgent", msg_manage)
        self.assertTrue(
            "ManagePatients" in msg_manage or "access denied" in msg_manage.lower() or "permission" in msg_manage.lower(),
            f"Unexpected manage permission message: {msg_manage}"
        )

if __name__ == "__main__":
    unittest.main()
