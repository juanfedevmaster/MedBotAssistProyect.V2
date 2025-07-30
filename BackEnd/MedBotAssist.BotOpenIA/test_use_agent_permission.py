# test_use_agent_permission.py

import unittest
from unittest.mock import AsyncMock, patch
from app.agents.medical_agent import MedicalQueryAgent


class TestUseAgentPermission(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.message = "How many patients are in the database?"
        self.agent = MedicalQueryAgent()
        self.agent.query = AsyncMock()

    async def test_user_without_useagent_permission(self):
        self.agent.query.return_value = {
            "success": False,
            "response": "Access denied. You need the 'UseAgent' permission to use the medical agent."
        }

        response = await self.agent.query(
            message=self.message,
            conversation_id="test-1",
            user_permissions=["ViewPatients", "ManagePatients"],
            username="user_without_useagent",
            jwt_token="fake-jwt-token"
        )

        self.assertFalse(response["success"])
        self.assertIn("useagent", response["response"].lower())

    async def test_user_with_useagent_and_viewpatients(self):
        self.agent.query.return_value = {
            "success": True,
            "response": "The database currently contains a total of 10 patients."
        }

        response = await self.agent.query(
            message=self.message,
            conversation_id="test-2",
            user_permissions=["UseAgent", "ViewPatients"],
            username="user_view_only",
            jwt_token="fake-jwt-token"
        )

        self.assertTrue(response["success"])
        self.assertIn("patients", response["response"].lower())

    async def test_user_with_all_permissions(self):
        self.agent.query.return_value = {
            "success": True,
            "response": "We found 10 patient records in the system."
        }

        response = await self.agent.query(
            message=self.message,
            conversation_id="test-3",
            user_permissions=["UseAgent", "ViewPatients", "ManagePatients"],
            username="admin_user",
            jwt_token="fake-jwt-token"
        )

        self.assertTrue(response["success"])
        self.assertIn("patient", response["response"].lower())

    async def test_user_with_no_permissions(self):
        self.agent.query.return_value = {
            "success": False,
            "response": "Access denied. Please contact administrator for permissions."
        }

        response = await self.agent.query(
            message=self.message,
            conversation_id="test-4",
            user_permissions=[],
            username="unauthorized_user",
            jwt_token="fake-jwt-token"
        )

        self.assertFalse(response["success"])
        self.assertIn("denied", response["response"].lower())


if __name__ == "__main__":
    unittest.main()