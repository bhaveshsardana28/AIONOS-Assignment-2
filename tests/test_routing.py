import unittest
from agent.router import AgentRouter

class TestRouter(unittest.TestCase):
    def setUp(self):
        self.router = AgentRouter()
    
    def test_guest_wifi_request(self):
        result = self.router.process_request(
            query="Can I get Wi-Fi for a guest tomorrow?",
            request_id="REQ-TEST-001",
            employee="Test Employee",
            email="test@example.com"
        )
        self.assertEqual(result["intent"], "Guest Wi-Fi")
        self.assertEqual(result["risk_level"], "LOW")
        self.assertEqual(result["recommended_action"], "RESOLVE")
        self.assertIsNone(result["ticket_id"])  # No ticket for guest Wi-Fi
        self.assertIn("front-desk kiosk", result['response'])
        self.assertIn("KB-07", result['response'])
    
    def test_security_incident_escalation(self):
        result = self.router.process_request(
            query="I got a phishing email asking for my password",
            request_id="REQ-TEST-002",
            employee="Test Employee",
            email="test@example.com"
        )
        self.assertEqual(result["intent"], "Security Incident")
        self.assertEqual(result["risk_level"], "HIGH")
        self.assertEqual(result["recommended_action"], "ESCALATE")
        self.assertIsNotNone(result["ticket_id"])
        self.assertEqual(result['ticket']['assigned_team'], "Security")
        response_lower = result['response'].lower()
        self.assertIn("security@veridian-corp.example", response_lower)
        self.assertIn("do not forward", response_lower)
        self.assertIn("KB-09", result['response'])
    
    def test_laptop_replacement_approval_needed(self):
        result = self.router.process_request(
            query="My laptop is dead after 3.5 years",
            request_id="REQ-TEST-003",
            employee="Test Employee",
            email="test@example.com"
        )
        self.assertEqual(result["intent"], "Laptop Replacement")
        self.assertEqual(result["risk_level"], "MEDIUM")
        self.assertEqual(result["recommended_action"], "ESCALATE")
        self.assertIsNotNone(result["ticket_id"])
        self.assertIn("finance sign-off", result['ticket']['required_approval'].lower())
        self.assertIn("less than 4 years old", result['response'])
        self.assertIn("KB-03", result['response'])
    
    def test_ambiguous_request_clarification(self):
        result = self.router.process_request(
            query="hey can you help, its not working",
            request_id="REQ-TEST-004",
            employee="Test Employee",
            email="test@example.com"
        )
        self.assertEqual(result["intent"], "Unknown / Ambiguous")
        self.assertEqual(result["risk_level"], "LOW")
        self.assertEqual(result["recommended_action"], "CLARIFY")
        self.assertIsNone(result["ticket_id"])
        self.assertIn("what isn't working", result['response'].lower())

if __name__ == '__main__':
    unittest.main()