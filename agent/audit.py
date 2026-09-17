import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import os

class AuditLogger:
    def __init__(self, audit_log_path: str = "data/audit_log.json"):
        self.audit_log_path = audit_log_path
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.audit_log_path), exist_ok=True)
        # Load existing audit log if exists
        self.audit_log = self._load_audit_log()
    
    def _load_audit_log(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.audit_log_path):
            try:
                with open(self.audit_log_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []
    
    def log_interaction(self,
                       request_id: str,
                       employee: str,
                       email: str,
                       input_query: str,
                       detected_intent: str,
                       retrieved_source: str,
                       decision: str,
                       risk_level: str,
                       action_taken: str,
                       ticket_id: Optional[str],
                       final_response: str,
                       reason: str) -> None:
        """
        Log an audit record.
        """
        audit_record = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "employee": employee,
            "email": email,
            "input": input_query,
            "detected_intent": detected_intent,
            "retrieved_source": retrieved_source,
            "decision": decision,
            "risk_level": risk_level,
            "action": action_taken,
            "ticket_id": ticket_id,
            "final_response": final_response,
            "reason": reason
        }
        self.audit_log.append(audit_record)
        self._save_audit_log()
    
    def _save_audit_log(self):
        with open(self.audit_log_path, 'w') as f:
            json.dump(self.audit_log, f, indent=2)
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        return self.audit_log

# For testing
if __name__ == "__main__":
    logger = AuditLogger()
    logger.log_interaction(
        request_id="REQ-01",
        employee="Aditi Sharma",
        email="aditi.sharma@veridian-corp.example",
        input_query="My laptop won’t turn on at all, it’s completely dead, had it about 3.5 years now.",
        detected_intent="Laptop Replacement",
        retrieved_source="KB-03",
        decision="ESCALATE",
        risk_level="MEDIUM",
        action_taken="Ticket created for approval",
        ticket_id="AI-1000",
        final_response="Your laptop is eligible for replacement but requires Finance sign-off and IT approval due to being less than 4 years old.",
        reason="Based on KB-03 and Asset Management Policy"
    )
    print("Audit logged")