class RiskEngine:
    def __init__(self):
        pass
    
    def assess_risk(self, intent: str, entities: dict, policy: dict) -> str:
        """
        Assess risk level based on intent, entities, and policy.
        Returns: LOW, MEDIUM, HIGH
        """
        # This is a simplified version. In reality, we would have more complex logic.
        # For now, we delegate to the policy engine's _apply_rules but we only return risk.
        # We'll duplicate the logic for simplicity.
        
        # Initialize
        risk_level = "LOW"
        
        # Rules per intent (same as in policy_engine)
        if intent == "Password Reset":
            if entities.get('password_attempts', 0) >= 5:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
        
        elif intent == "VPN Access":
            if entities.get('employee_type') == 'contractor':
                risk_level = "MEDIUM"
            elif entities.get('vpn_expired'):
                risk_level = "LOW"
            else:
                risk_level = "LOW"
        
        elif intent == "Laptop Replacement":
            laptop_years = entities.get('laptop_years', 0)
            hardware_failure = entities.get('hardware_failure_indicated', False)
            
            if laptop_years >= 3 or hardware_failure:
                if laptop_years < 4:
                    risk_level = "MEDIUM"
                else:
                    risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
        
        elif intent == "Hardware Issue":
            risk_level = "LOW"
        
        elif intent == "Software Installation":
            risk_level = "MEDIUM"
        
        elif intent == "Printer Issue":
            risk_level = "LOW"
        
        elif intent == "Mailbox Quota":
            risk_level = "LOW"
        
        elif intent == "Guest Wi-Fi":
            risk_level = "LOW"
        
        elif intent == "Expense Tool":
            risk_level = "LOW"
        
        elif intent == "Security Incident":
            risk_level = "HIGH"
        
        elif intent == "Home Office Equipment":
            wfh_days = entities.get('wfh_days_per_week', 0)
            if wfh_days > 3:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
        
        elif intent == "Access Request":
            risk_level = "HIGH"
        
        else:  # Unknown / Ambiguous
            risk_level = "LOW"
        
        return risk_level

# For testing
if __name__ == "__main__":
    engine = RiskEngine()
    print(engine.assess_risk("Laptop Replacement", {"laptop_years": 3.5, "hardware_failure_indicated": True}, {}))