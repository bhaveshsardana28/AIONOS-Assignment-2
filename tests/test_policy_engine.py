import unittest
from agent.policy_engine import PolicyEngine
from agent.llm import LLMHandler
from agent.retrieval import PolicyRetriever

class TestPolicyEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PolicyEngine()
        self.llm_handler = LLMHandler()
        self.retriever = PolicyRetriever()
    
    def test_password_reset_low_risk(self):
        query = "I forgot my password, can you help me reset it?"
        intent, policy, risk, action, entities = self.engine.evaluate_request(query)
        self.assertEqual(intent, "Password Reset")
        self.assertEqual(risk, "LOW")
        self.assertEqual(action, "RESOLVE")
        self.assertLess(entities.get('password_attempts', 0), 5)
    
    def test_password_reset_high_attempts_escalate(self):
        query = "I tried my password 10 times and now I'm locked out"
        intent, policy, risk, action, entities = self.engine.evaluate_request(query)
        self.assertEqual(intent, "Password Reset")
        self.assertEqual(entities.get('password_attempts'), 10)
        self.assertEqual(risk, "MEDIUM")
        self.assertEqual(action, "ESCALATE")
    
    def test_vpn_contractor_requires_approval(self):
        query = "I am a contractor and need VPN access"
        intent, policy, risk, action, entities = self.engine.evaluate_request(query)
        self.assertEqual(intent, "VPN Access")
        self.assertEqual(entities.get('employee_type'), 'contractor')
        self.assertEqual(risk, "MEDIUM")
        self.assertEqual(action, "ESCALATE")
    
    def test_vpn_expired_guidance(self):
        query = "My VPN says my credentials have expired"
        intent, policy, risk, action, entities = self.engine.evaluate_request(query)
        self.assertEqual(intent, "VPN Access")
        self.assertEqual(entities.get('vpn_expired'), True)
        self.assertEqual(risk, "LOW")
        self.assertEqual(action, "RESOLVE")
    
    def test_laptop_replacement_early_needs_approval(self):
        query = "My laptop is broken and I've had it for 3 years"
        intent, policy, risk, action, entities = self.engine.evaluate_request(query)
        self.assertEqual(intent, "Laptop Replacement")
        self.assertEqual(entities.get('laptop_years'), 3.0)
        self.assertEqual(entities.get('hardware_failure_indicated'), True)
        self.assertEqual(risk, "MEDIUM")
        self.assertEqual(action, "ESCALATE")
    
    def test_laptop_replacement_late_approval(self):
        query = "I need a new laptop, mine is 5 years old"
        intent, policy, risk, action, entities = self.engine.evaluate_request(query)
        self.assertEqual(intent, "Laptop Replacement")
        self.assertEqual(entities.get('laptop_years'), 5.0)
        self.assertEqual(risk, "MEDIUM")
        self.assertEqual(action, "ESCALATE")
    
    def test_guest_wifi_no_ticket(self):
        query = "Can I get guest Wi-Fi for a visitor?"
        intent, policy, risk, action, entities = self.engine.evaluate_request(query)
        self.assertEqual(intent, "Guest Wi-Fi")
        self.assertEqual(risk, "LOW")
        self.assertEqual(action, "RESOLVE")
    
    def test_security_incident_high_risk(self):
        query = "I think I received a phishing email"
        intent, policy, risk, action, entities = self.engine.evaluate_request(query)
        self.assertEqual(intent, "Security Incident")
        self.assertEqual(risk, "HIGH")
        self.assertEqual(action, "ESCALATE")
    
    def test_ambiguous_request_clarify(self):
        query = "help me"
        intent, policy, risk, action, entities = self.engine.evaluate_request(query)
        self.assertEqual(intent, "Unknown / Ambiguous")
        self.assertEqual(risk, "LOW")
        self.assertEqual(action, "CLARIFY")

if __name__ == '__main__':
    unittest.main()