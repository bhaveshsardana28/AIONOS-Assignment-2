import unittest
from agent.router import AgentRouter

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.router = AgentRouter()
    
    def test_phishing_email_reporting(self):
        result = self.router.process_request(
            query="I received a suspicious email asking for my login credentials",
            request_id="REQ-SEC-001",
            employee="Security Test",
            email="security@example.com"
        )
        self.assertEqual(result['intent'], "Security Incident")
        self.assertEqual(result['risk_level'], "HIGH")
        self.assertEqual(result['recommended_action'], "ESCALATE")
        self.assertIsNotNone(result['ticket_id'])
        # Check that the response contains the required security guidance
        response = result['response'].lower()
        self.assertIn("security@veridian-corp.example", response)
        self.assertIn("do not forward", response)
        self.assertIn("immediately", response)
        # Check ticket details
        ticket = result['ticket']
        self.assertEqual(ticket['assigned_team'], "Security")
        self.assertEqual(ticket['risk_level'], "HIGH")
        self.assertEqual(ticket['recommended_action'], "ESCALATE")
        self.assertEqual(ticket['source_policy'], "KB-09")
    
    def test_malware_suspicion(self):
        result = self.router.process_request(
            query="I think my computer has malware, it's running very slow",
            request_id="REQ-SEC-002",
            employee="Security Test",
            email="security@example.com"
        )
        self.assertEqual(result['intent'], "Security Incident")
        self.assertEqual(result['risk_level'], "HIGH")
        self.assertEqual(result['recommended_action'], "ESCALATE")
        self.assertIn("security@veridian-corp.example", result['response'].lower())
        self.assertIn("do not forward", result['response'].lower())
    
    def test_unauthorized_access_attempt(self):
        result = self.router.process_request(
            query="I got a notification about an unauthorized access attempt on my account",
            request_id="REQ-SEC-003",
            employee="Security Test",
            email="security@example.com"
        )
        self.assertEqual(result['intent'], "Security Incident")
        self.assertEqual(result['risk_level'], "HIGH")
        self.assertEqual(result['recommended_action'], "ESCALATE")
        self.assertIn("security@veridian-corp.example", result['response'].lower())
        self.assertIn("do not forward", result['response'].lower())
    
    def test_security_incident_not_forwarded_warning(self):
        # Ensure the warning about not forwarding is always present
        queries = [
            "I think I got a phishing email",
            "There's malware on my computer",
            "Someone tried to access my account without permission"
        ]
        for query in queries:
            result = self.router.process_request(
                query=query,
                request_id=f"REQ-SEC-{hash(query) % 10000}",
                employee="Security Test",
                email="security@example.com"
            )
            self.assertIn("do not forward", result['response'].lower(), 
                         f"Missing 'do not forward' warning for query: {query}")

if __name__ == '__main__':
    unittest.main()