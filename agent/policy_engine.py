from typing import Dict, Any, Tuple, Optional
import re
from .retrieval import PolicyRetriever

class PolicyEngine:
    def __init__(self):
        self.retriever = PolicyRetriever()
    
    def extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract relevant entities from the query."""
        entities = {}
        query_lower = query.lower()
        
        # Extract years of laptop
        years_match = re.search(r'(\d+\.?\d*)|(\d*\.\d+)', query_lower)
        if years_match:
            # Determine which group matched
            if years_match.group(1) is not None:
                num_str = years_match.group(1)
            else:
                num_str = years_match.group(2)
            try:
                entities['laptop_years'] = float(num_str)
            except ValueError:
                pass
        
        # Check for contractor
        if 'contractor' in query_lower:
            entities['employee_type'] = 'contractor'
        elif 'full-time' in query_lower or 'full time' in query_lower:
            entities['employee_type'] = 'full-time'
        else:
            # Default to full-time if not specified? But we should not assume.
            # We'll leave it unset and let the policy engine handle.
            pass
        
        # Check for hardware failure keywords
        failure_keywords = ['dead', "won't turn on", 'not turning on', 'broken', 'failed', 'faulty']
        for keyword in failure_keywords:
            if keyword in query_lower:
                entities['hardware_failure_indicated'] = True
                break
        
        # Check for printer asset tag request
        if 'asset tag' in query_lower:
            entities['asset_tag_requested'] = True
        
        # Check for expired credentials
        if 'expired' in query_lower and ('vpn' in query_lower or 'credential' in query_lower):
            entities['vpn_expired'] = True
        
        # Check for password attempts
        attempts_match = re.search(r'(\d+)\s*times?', query_lower)
        if attempts_match and ('password' in query_lower or 'account' in query_lower):
            try:
                entities['password_attempts'] = int(attempts_match.group(1))
            except ValueError:
                pass
        
        # Check for mailbox quota
        if 'mailbox' in query_lower and ('full' in query_lower or 'quota' in query_lower):
            entities['mailbox_full'] = True
        
        # Check for phishing
        if 'phishing' in query_lower or 'suspected phishing' in query_lower:
            entities['phishing_suspected'] = True
        
        # Check for work from home frequency
        wfh_match = re.search(r'((\d+\.?\d*)|(\d*\.\d+))\s*days?\s*(?:per\s+|\/?|a\s+)?week', query_lower)
        if wfh_match:
            # Determine which group matched for the number
            if wfh_match.group(2) is not None:
                num_str = wfh_match.group(2)
            else:
                num_str = wfh_match.group(3)
            try:
                entities['wfh_days_per_week'] = int(num_str)
            except ValueError:
                pass
        
        # Check for expense tool
        if 'expense' in query_lower and ('tool' in query_lower or 'login' in query_lower):
            entities['expense_tool_issue'] = True
        
        # Check for admin access
        if 'admin access' in query_lower or 'privileged access' in query_lower:
            entities['admin_access_request'] = True
        
        # Check for guest Wi-Fi
        if 'guest' in query_lower and 'wi-fi' in query_lower:
            entities['guest_wifi_request'] = True
        
        return entities
    
    def evaluate_request(self, query: str) -> Tuple[str, Dict[str, Any], str, str, Dict[str, Any]]:
        """
        Evaluate the request and return:
        - intent: one of the predefined intents
        - policy: the retrieved policy dictionary
        - risk_level: LOW, MEDIUM, HIGH
        - recommended_action: one of RESOLVE, CLARIFY, ESCALATE
        Also returns the retrieved policy and confidence? We'll return the policy and we can get confidence from retriever separately.
        We'll also return the entities for use in decision making.
        """
        # Retrieve policy
        policy, confidence = self.retriever.retrieve(query)
        entities = self.extract_entities(query)
        
        # Determine intent based on policy and entities
        intent = self._determine_intent(query, policy, entities)
        
        # Apply deterministic rules to get risk and action
        risk_level, recommended_action = self._apply_rules(intent, entities, policy)
        
        return intent, policy, risk_level, recommended_action, entities
    
    def _determine_intent(self, query: str, policy: Dict[str, Any], entities: Dict[str, Any]) -> str:
        """Determine the intent based on query, policy, and entities."""
        query_lower = query.lower()
        policy_title = policy.get('title', '').lower()
        
        # Check for specific intents based on keywords
        if 'password' in query_lower and ('reset' in query_lower or 'locked' in query_lower or 'attempt' in query_lower):
            return "Password Reset"
        elif 'vpn' in query_lower:
            return "VPN Access"
        elif 'laptop' in query_lower:
            laptop_years = entities.get('laptop_years', 0)
            if laptop_years >= 3:
                return "Laptop Replacement"
            elif any(kw in query_lower for kw in ['broken', 'not working', 'dead', 'won\'t turn on', 'flickering', 'screen', 'hardware']) or entities.get('hardware_failure_indicated', False):
                return "Hardware Issue"
            elif any(kw in query_lower for kw in ['replace', 'replacement', 'new', 'upgrade']):
                return "Laptop Replacement"
            else:
                return "Unknown / Ambiguous"
                return "Unknown / Ambiguous"
        elif ('software' in query_lower or 'extension' in query_lower) and ('install' in query_lower or 'approval' in query_lower):
            return "Software Installation"
        elif 'printer' in query_lower or 'print' in query_lower:
            return "Printer Issue"
        elif ('mailbox' in query_lower or 'email' in query_lower) and any(kw in query_lower for kw in ['quota', 'full', 'limit', 'size']):
            return "Mailbox Quota"
        elif 'guest' in query_lower and 'wi-fi' in query_lower:
            return "Guest Wi-Fi"
        elif 'expense' in query_lower:
            return "Expense Tool"
        elif 'phishing' in query_lower or 'malware' in query_lower or (('unauthorized' in query_lower or 'without permission' in query_lower) and 'access' in query_lower) or ('suspicious' in query_lower and 'email' in query_lower):
            return "Security Incident"
        elif ('work from home' in query_lower or 'working from home' in query_lower or 'remote' in query_lower) and any(kw in query_lower for kw in ['monitor', 'chair', 'equipment']):
            return "Home Office Equipment"
        elif 'admin' in query_lower and 'access' in query_lower:
            return "Access Request"
        else:
            # Default to unknown
            return "Unknown / Ambiguous"
    
    def _apply_rules(self, intent: str, entities: Dict[str, Any], policy: Dict[str, Any]) -> Tuple[str, str]:
        """
        Apply deterministic rules based on intent and entities.
        Returns (risk_level, recommended_action)
        risk_level: LOW, MEDIUM, HIGH
        recommended_action: RESOLVE, CLARIFY, ESCALATE
        """
        # Initialize
        risk_level = "LOW"
        recommended_action = "RESOLVE"
        
        # Rules per intent
        if intent == "Password Reset":
            if entities.get('password_attempts', 0) >= 5:
                # After 5 failed attempts, contact IT to unlock manually
                risk_level = "MEDIUM"  # Requires IT intervention but not high risk
                recommended_action = "ESCALATE"  # Because it requires manual unlock by IT
            else:
                # Can self-service
                recommended_action = "RESOLVE"
        
        elif intent == "VPN Access":
            if entities.get('employee_type') == 'contractor':
                # Contractors require manager approval
                risk_level = "MEDIUM"
                recommended_action = "ESCALATE"  # Needs manager approval
            elif entities.get('vpn_expired'):
                # VPN credentials expired - employee must renew themselves
                recommended_action = "RESOLVE"  # Inform them to renew
            else:
                # Automatic for full-time
                recommended_action = "RESOLVE"
        
        elif intent == "Laptop Replacement":
            laptop_years = entities.get('laptop_years', 0)
            hardware_failure = entities.get('hardware_failure_indicated', False)
            
            # Check KB-03: eligible after 3 years or earlier with verified hardware failure
            if laptop_years >= 3 or hardware_failure:
                # But check Asset Management Policy: early replacement outside 4-year cycle requires Finance + IT
                if laptop_years < 4:
                    # Early replacement (less than 4 years) requires Finance sign-off and IT approval
                    risk_level = "MEDIUM"
                    recommended_action = "ESCALATE"  # Needs approvals
                else:
                    # Beyond 4 years, just IT approval? Actually policy says standard 4-year cycle.
                    # But KB-03 says eligible after 3 years, so beyond 4 is certainly eligible.
                    # However, asset policy says early replacement outside 4-year cycle requires Finance + IT.
                    # If it's beyond 4 years, it's not early, so maybe just IT? But we don't have a policy for beyond 4.
                    # We'll assume that beyond 4 years, it's just eligible and requires IT approval (like a standard request).
                    # But to be safe, we'll say it requires IT approval (which is medium risk?).
                    # Actually, the asset policy says early replacement outside 4-year cycle requires Finance + IT.
                    # If it's not early (>=4 years), then it doesn't require Finance? But we don't have a policy that says beyond 4 is automatic.
                    # We'll treat it as requiring IT approval (so medium).
                    risk_level = "MEDIUM"
                    recommended_action = "ESCALATE"
            else:
                # Not eligible based on years and no hardware failure indicated
                risk_level = "LOW"
                recommended_action = "CLARIFY"  # Need to ask about hardware failure or wait until eligible
        
        elif intent == "Hardware Issue":
            # For hardware issues, we first troubleshoot unless it's a replacement request
            # Since we already have a separate intent for laptop replacement, we treat this as repair/troubleshooting
            # We don't have a specific policy for hardware troubleshooting, but we can advise basic steps?
            # However, the policies don't cover general hardware troubleshooting.
            # We'll treat it as needing clarification or escalation to IT for diagnosis.
            risk_level = "LOW"
            recommended_action = "CLARIFY"  # Ask for more details or suggest basic troubleshooting
        
        elif intent == "Software Installation":
            # We don't have info if software is in catalog or not from the query.
            # We'll need to ask.
            risk_level = "MEDIUM"
            recommended_action = "CLARIFY"  # Ask if software is in approved catalog
        
        elif intent == "Printer Issue":
            # Policy: check queue, restart spooler, if persists then ticket with asset tag
            # We'll ask if they've done the first two steps.
            risk_level = "LOW"
            recommended_action = "CLARIFY"  # Ask if they've checked queue and restarted spooler
        
        elif intent == "Mailbox Quota":
            # Default quota 25GB, archive old mail, increases above 25GB require manager approval up to 50GB
            # We don't know current usage, so we advise to archive.
            recommended_action = "RESOLVE"  # We can give the advice without clarification
            risk_level = "LOW"
        
        elif intent == "Guest Wi-Fi":
            # Employee can generate from kiosk, valid 24 hours, no IT ticket
            recommended_action = "RESOLVE"
            risk_level = "LOW"
        
        elif intent == "Expense Tool":
            # IT can only assist with login/technical issues once account exists.
            # We need to know if account exists.
            risk_level = "LOW"
            recommended_action = "CLARIFY"  # Ask if they have an account
        
        elif intent == "Security Incident":
            # High risk, must report to security@veridian-corp.example and not forward
            risk_level = "HIGH"
            recommended_action = "ESCALATE"
        
        elif intent == "Home Office Equipment":
            # Eligible if WFH > 3 days/week, requires manager sign-off and Finance processing, IT ships after approval
            wfh_days = entities.get('wfh_days_per_week', 0)
            if wfh_days > 3:
                risk_level = "MEDIUM"  # Requires approvals
                recommended_action = "ESCALATE"
            else:
                # Not eligible
                risk_level = "LOW"
                recommended_action = "RESOLVE"  # Inform not eligible
        
        elif intent == "Access Request":
            # Privileged access request - treat as high risk unless we have more info
            risk_level = "HIGH"
            recommended_action = "ESCALATE"
        
        else:  # Unknown / Ambiguous
            risk_level = "LOW"
            recommended_action = "CLARIFY"  # Ask for clarification
        
        return risk_level, recommended_action

# For testing
if __name__ == "__main__":
    engine = PolicyEngine()
    query = "My laptop won’t turn on at all, it’s completely dead, had it about 3.5 years now."
    intent, policy, risk, action, entities = engine.evaluate_request(query)
    print(f"Query: {query}")
    print(f"Intent: {intent}")
    print(f"Policy: {policy['id']} - {policy['title']}")
    print(f"Risk: {risk}")
    print(f"Action: {action}")
    print(f"Entities: {entities}")