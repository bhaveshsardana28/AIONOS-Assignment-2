import unittest
from agent.router import AgentRouter

class TestEmployeeRequests(unittest.TestCase):
    def setUp(self):
        self.router = AgentRouter()
        # Load the employee requests to test them
        import json
        with open('data/employee_requests.json', 'r') as f:
            self.requests = json.load(f)
    
    def test_req_01_laptop_dead_3_5_years(self):
        req = self.requests[0]  # REQ-01
        result = self.router.process_request(
            query=req['request'],
            request_id=req['id'],
            employee=req['employee'],
            email=req['email']
        )
        # Should be Laptop Replacement, MEDIUM risk, ESCALATE (needs approvals)
        self.assertEqual(result['intent'], "Laptop Replacement")
        self.assertEqual(result['risk_level'], "MEDIUM")
        self.assertEqual(result['recommended_action'], "ESCALATE")
        self.assertIsNotNone(result['ticket_id'])
        self.assertIn("finance sign-off", result['ticket']['required_approval'].lower())
        self.assertIn("less than 4 years old", result['response'])
    
    def test_req_02_guest_wifi_tomorrow(self):
        req = self.requests[1]  # REQ-02
        result = self.router.process_request(
            query=req['request'],
            request_id=req['id'],
            employee=req['employee'],
            email=req['email']
        )
        # Should be Guest Wi-Fi, LOW risk, RESOLVE, no ticket
        self.assertEqual(result['intent'], "Guest Wi-Fi")
        self.assertEqual(result['risk_level'], "LOW")
        self.assertEqual(result['recommended_action'], "RESOLVE")
        self.assertIsNone(result['ticket_id'])
        self.assertIn("front-desk kiosk", result['response'])
        self.assertIn("KB-07", result['response'])
    
    def test_req_03_locked_out_6_attempts(self):
        req = self.requests[2]  # REQ-03
        result = self.router.process_request(
            query=req['request'],
            request_id=req['id'],
            employee=req['employee'],
            email=req['email']
        )
        # Should be Password Reset, MEDIUM risk, ESCALATE (>=5 attempts)
        self.assertEqual(result['intent'], "Password Reset")
        self.assertEqual(result['risk_level'], "MEDIUM")
        self.assertEqual(result['recommended_action'], "ESCALATE")
        self.assertIsNotNone(result['ticket_id'])
        self.assertGreaterEqual(result['entities'].get('password_attempts', 0), 5)
    
    def test_req_04_non_catalog_software(self):
        req = self.requests[3]  # REQ-04
        result = self.router.process_request(
            query=req['request'],
            request_id=req['id'],
            employee=req['employee'],
            email=req['email']
        )
        # Should be Software Installation, MEDIUM risk, CLARIFY (need to check if in catalog)
        self.assertEqual(result['intent'], "Software Installation")
        self.assertEqual(result['risk_level'], "MEDIUM")
        self.assertEqual(result['recommended_action'], "CLARIFY")
        self.assertIsNone(result['ticket_id'])
        self.assertIn("approved catalog", result['response'])
    
    def test_req_05_vpn_expired_credentials(self):
        req = self.requests[4]  # REQ-05
        result = self.router.process_request(
            query=req['request'],
            request_id=req['id'],
            employee=req['employee'],
            email=req['email']
        )
        # Should be VPN Access, LOW risk, RESOLVE (guidance to renew)
        self.assertEqual(result['intent'], "VPN Access")
        self.assertEqual(result['risk_level'], "LOW")
        self.assertEqual(result['recommended_action'], "RESOLVE")
        self.assertIsNone(result['ticket_id'])
        self.assertIn("renewed by the employee", result['response'])
        self.assertIn("KB-02", result['response'])
    
    def test_req_06_printer_paper_jam_no_jam(self):
        req = self.requests[5]  # REQ-06
        result = self.router.process_request(
            query=req['request'],
            request_id=req['id'],
            employee=req['employee'],
            email=req['email']
        )
        # Should be Printer Issue, LOW risk, CLARIFY (ask about troubleshooting steps)
        self.assertEqual(result['intent'], "Printer Issue")
        self.assertEqual(result['risk_level'], "LOW")
        self.assertEqual(result['recommended_action'], "CLARIFY")
        self.assertIsNone(result['ticket_id'])
        self.assertIn("printer queue", result['response'])
        self.assertIn("restart the print spooler", result['response'])
    
    def test_req_07_wfh_4_days_monitor(self):
        req = self.requests[6]  # REQ-07
        result = self.router.process_request(
            query=req['request'],
            request_id=req['id'],
            employee=req['employee'],
            email=req['email']
        )
        # Should be Home Office Equipment, MEDIUM risk, ESCALATE (needs approvals)
        self.assertEqual(result['intent'], "Home Office Equipment")
        self.assertEqual(result['risk_level'], "MEDIUM")
        self.assertEqual(result['recommended_action'], "ESCALATE")
        self.assertIsNotNone(result['ticket_id'])
        self.assertIn("manager sign-off", result['ticket']['required_approval'].lower())
        self.assertIn("finance processing", result['ticket']['required_approval'].lower())
        self.assertIn("KB-10", result['response'])
    
    def test_req_08_phishing_email_forwarding(self):
        req = self.requests[7]  # REQ-08
        result = self.router.process_request(
            query=req['request'],
            request_id=req['id'],
            employee=req['employee'],
            email=req['email']
        )
        # Should be Security Incident, HIGH risk, ESCALATE
        self.assertEqual(result['intent'], "Security Incident")
        self.assertEqual(result['risk_level'], "HIGH")
        self.assertEqual(result['recommended_action'], "ESCALATE")
        self.assertIsNotNone(result['ticket_id'])
        self.assertIn("security@veridian-corp.example", result['response'])
        self.assertIn("do not forward", result['response'].lower())
        self.assertIn("KB-09", result['response'])
    
    def test_req_09_mailbox_full(self):
        req = self.requests[8]  # REQ-09
        result = self.router.process_request(
            query=req['request'],
            request_id=req['id'],
            employee=req['employee'],
            email=req['email']
        )
        # Should be Mailbox Quota, LOW risk, RESOLVE (archive guidance)
        self.assertEqual(result['intent'], "Mailbox Quota")
        self.assertEqual(result['risk_level'], "LOW")
        self.assertEqual(result['recommended_action'], "RESOLVE")
        self.assertIsNone(result['ticket_id'])
        self.assertIn("archive old mail", result['response'])
        self.assertIn("KB-06", result['response'])
    
    def test_req_10_admin_access_finance_server(self):
        req = self.requests[9]  # REQ-10
        result = self.router.process_request(
            query=req['request'],
            request_id=req['id'],
            employee=req['employee'],
            email=req['email']
        )
        # Should be Access Request, HIGH risk, ESCALATE (privileged access)
        self.assertEqual(result['intent'], "Access Request")
        self.assertEqual(result['risk_level'], "HIGH")
        self.assertEqual(result['recommended_action'], "ESCALATE")
        self.assertIsNotNone(result['ticket_id'])
        self.assertIn("security approval", result['ticket']['required_approval'].lower())
        self.assertIn("business justification", result['ticket']['required_approval'].lower())
        self.assertIn("Admin access requests require", result['response'])
    
    def test_req_11_contractor_needs_vpn(self):
        req = self.requests[10]  # REQ-11
        result = self.router.process_request(
            query=req['request'],
            request_id=req['id'],
            employee=req['employee'],
            email=req['email']
        )
        # Should be VPN Access, MEDIUM risk, ESCALATE (contractor needs manager approval)
        self.assertEqual(result['intent'], "VPN Access")
        self.assertEqual(result['risk_level'], "MEDIUM")
        self.assertEqual(result['recommended_action'], "ESCALATE")
        self.assertIsNotNone(result['ticket_id'])
        self.assertEqual(result['entities'].get('employee_type'), 'contractor')
        self.assertIn("manager approval", result['ticket']['required_approval'].lower())
        self.assertIn("access request form", result['response'])
    
    def test_req_12_expense_tool_login_failure(self):
        req = self.requests[11]  # REQ-12
        result = self.router.process_request(
            query=req['request'],
            request_id=req['id'],
            employee=req['employee'],
            email=req['email']
        )
        # Should be Expense Tool, LOW risk, CLARIFY (ask if account exists)
        self.assertEqual(result['intent'], "Expense Tool")
        self.assertEqual(result['risk_level'], "LOW")
        self.assertEqual(result['recommended_action'], "CLARIFY")
        self.assertIsNone(result['ticket_id'])
        self.assertIn("expense management tool", result['response'])
        self.assertIn("do you already have an account", result['response'].lower())
    
    def test_req_13_laptop_screen_flickering_2_years(self):
        req = self.requests[12]  # REQ-13
        result = self.router.process_request(
            query=req['request'],
            request_id=req['id'],
            employee=req['employee'],
            email=req['email']
        )
        # Should be Hardware Issue, LOW risk, CLARIFY (troubleshooting first)
        self.assertEqual(result['intent'], "Hardware Issue")
        self.assertEqual(result['risk_level'], "LOW")
        self.assertEqual(result['recommended_action'], "CLARIFY")
        self.assertIsNone(result['ticket_id'])
        self.assertIn("troubleshooting", result['response'].lower())
    
    def test_req_14_browser_extension_productivity(self):
        req = self.requests[13]  # REQ-14
        result = self.router.process_request(
            query=req['request'],
            request_id=req['id'],
            employee=req['employee'],
            email=req['email']
        )
        # Should be Software Installation, MEDIUM risk, CLARIFY (not in catalog by default)
        self.assertEqual(result['intent'], "Software Installation")
        self.assertEqual(result['risk_level'], "MEDIUM")
        self.assertEqual(result['recommended_action'], "CLARIFY")
        self.assertIsNone(result['ticket_id'])
        self.assertIn("approved catalog", result['response'])
    
    def test_req_15_ambiguous_not_working(self):
        req = self.requests[14]  # REQ-15
        result = self.router.process_request(
            query=req['request'],
            request_id=req['id'],
            employee=req['employee'],
            email=req['email']
        )
        # Should be Unknown / Ambiguous, LOW risk, CLARIFY (ask for details)
        self.assertEqual(result['intent'], "Unknown / Ambiguous")
        self.assertEqual(result['risk_level'], "LOW")
        self.assertEqual(result['recommended_action'], "CLARIFY")
        self.assertIsNone(result['ticket_id'])
        self.assertIn("what isn't working", result['response'])

if __name__ == '__main__':
    unittest.main()