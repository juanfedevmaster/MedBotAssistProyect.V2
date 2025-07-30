# test_import_structure.py
import pytest

@pytest.mark.imports
def test_permission_validators_import():
    from app.agents.tools.permission_validators import (
        check_use_agent_permission,
        check_view_patients_permission,
        check_create_patients_permission,
        validate_patient_view_permissions,
        validate_patient_management_permissions
    )
    has_permission, error_msg = check_use_agent_permission()
    assert isinstance(has_permission, bool)
    assert isinstance(error_msg, str)
    assert "UseAgent" in error_msg or has_permission is True

@pytest.mark.imports
def test_patient_search_tools_import():
    import app.agents.tools.patient_search_tools

@pytest.mark.imports
def test_patient_management_tools_import():
    import app.agents.tools.patient_management_tools

@pytest.mark.imports
def test_main_package_import():
    import app.agents.tools
    assert hasattr(app.agents.tools, "__all__")

@pytest.mark.imports
def test_validate_patient_view_permissions_format():
    from app.agents.tools.permission_validators import validate_patient_view_permissions
    result = validate_patient_view_permissions()
    assert isinstance(result, tuple)
    assert len(result) == 2
    has_permission, error_msg = result
    assert isinstance(has_permission, bool)
    assert isinstance(error_msg, str)

@pytest.mark.structure
def test_permission_module_structure():
    import app.agents.tools.permission_validators as pv
    expected = [
        'check_use_agent_permission',
        'check_view_patients_permission',
        'check_create_patients_permission',
        'validate_patient_view_permissions',
        'validate_patient_management_permissions'
    ]
    for name in expected:
        assert hasattr(pv, name), f"{name} not found in permission_validators"

@pytest.mark.backwards
def test_backwards_compatibility_all_tools():
    from app.agents.tools import ALL_TOOLS
    assert isinstance(ALL_TOOLS, list)
    assert len(ALL_TOOLS) > 0
    for tool in ALL_TOOLS[:3]:  # Only check first 3
        assert hasattr(tool, 'name')
        assert isinstance(tool.name, str)
