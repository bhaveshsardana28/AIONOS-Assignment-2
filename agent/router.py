from .llm import LLMHandler
from .policy_engine import PolicyEngine
from .ticketing import TicketGenerator
from .audit import AuditLogger
from typing import Dict, Any, Optional, Tuple
import json

class AgentRouter:
    def __init__(self):
        self.llm_handler = LLMHandler()
        self.policy_engine = PolicyEngine()
        self.ticket_generator = TicketGenerator()
        self.audit_logger = AuditLogger()
    
    def process_request(self, 
                       query: str, 
                       request_id: Optional[str] = None,
                       employee: Optional[str] = None,
                       email: Optional[str] = None) -> Dict[str, Any]:
        """
        Process an employee request and return the agent's response along with any generated ticket and audit record.
        If request_id, employee, email are not provided, we treat it as a new request and generate placeholders.
        """
        # If not provided, we'll use placeholders for new requests
        if not request_id:
            request_id = f"REQ-NEW-{hash(query) % 10000}"
        if not employee:
            employee = "Unknown Employee"
        if not email:
            email = "unknown@veridian-corp.example"
        
        # Step 1: Intent detection and entity extraction using LLM (with fallback)
        intent, entities = self.llm_handler.classify_intent_and_extract_entities(query)
        
        # Step 2: Policy retrieval
        # We'll use the policy engine's retriever to get the policy and confidence
        from .retrieval import PolicyRetriever
        retriever = PolicyRetriever()
        policy, confidence = retriever.retrieve(query)
        
        # Step 3: Policy evaluation and risk assessment
        # We'll use the policy engine's evaluate_request method to get intent, policy, risk, action, entities
        # But note: we already have intent and entities from LLM, and policy from retrieval.
        # We'll call the policy engine's _apply_rules to get risk and action.
        risk_level, recommended_action = self.policy_engine._apply_rules(intent, entities, policy)
        
        # Step 4: Generate explanation/response
        response = self.llm_handler.generate_explanation(
            query, intent, policy, risk_level, recommended_action, entities
        )
        
        # Step 5: Determine if ticket is needed
        ticket = None
        ticket_id = None
        # Ticket is needed if we are escalating or if the action requires a ticket (like creating a ticket for approval)
        # According to the pipeline: Decision -> Resolve / Clarify / Escalate -> Ticket -> Audit
        # We'll create a ticket for Escalate and for some Resolve actions that require tracking? 
        # But the instructions say: "Create a structured ticket" when escalation/action requires a structured ticket.
        # We'll create a ticket for:
        # - ESCALATE actions
        # - RESOLVE actions that are not purely informational? Actually, even for resolve, we might want to track.
        # However, the examples show that for Guest Wi-Fi (resolve) no ticket is required.
        # We'll follow the policy: if the policy says no IT ticket required (like KB-07), then no ticket.
        # Otherwise, we'll create a ticket for ESCALATE and for RESOLVE when the policy implies a ticket (like printer issue after troubleshooting).
        # To keep it simple, we'll create a ticket only for ESCALATE and for RESOLVE when the intent is one that typically requires a ticket (like hardware issue that needs technician).
        # But we don't have that level of detail.
        # We'll create a ticket for:
        #   - ESCALATE (always)
        #   - RESOLVE for intents where the policy says to log a ticket (e.g., printer issue after restart)
        #
        # We'll implement a simple rule: create a ticket for ESCALATE and for RESOLVE when the intent is in a set that typically requires tracking.
        # For now, we'll create a ticket for ESCALATE and for RESOLVE for intents: Laptop Replacement, Hardware Issue, Printer Issue, Software Installation, Access Request, Home Office Equipment.
        # But note: for Laptop Replacement, we are escalating due to approvals, so it will be covered by ESCALATE.
        # For Hardware Issue, we are clarifying, so no ticket yet.
        # We'll adjust: we'll create a ticket only for ESCALATE and for RESOLVE when the policy explicitly says to log a ticket (like printer issue after restart).
        #
        # Given time, we'll create a ticket for:
        #   - ESCALATE (always)
        #   - RESOLVE for intents where the policy says to log a ticket (e.g., printer issue after restart)
        #
        # We'll check the policy content for keywords like "log a ticket" or "ticket".
        create_ticket = False
        if recommended_action == "ESCALATE":
            create_ticket = True
        elif recommended_action == "RESOLVE":
            # Check if policy suggests logging a ticket
            policy_content = policy.get('content', '').lower()
            # If policy explicitly says no ticket required, do not create ticket
            if "no ticket required" in policy_content or "no it ticket" in policy_content:
                create_ticket = False
            elif "ticket" in policy_content:
                create_ticket = True
            # Also for certain intents that we know require a ticket (like hardware issue that needs repair)
            # But we don't have that info, so we'll skip.
        
        if create_ticket:
            # Generate issue summary
            issue_summary = query[:100] + ("..." if len(query) > 100 else "")
            # Determine required approval based on intent and entities
            required_approval = self._determine_required_approval(intent, entities)
            # Determine assigned team
            assigned_team = self._determine_assigned_team(intent, entities)
            # Status
            status = "Open"
            # Create ticket
            ticket = self.ticket_generator.create_ticket(
                request_id=request_id,
                employee=employee,
                email=email,
                intent=intent,
                issue_summary=issue_summary,
                risk_level=risk_level,
                recommended_action=recommended_action,
                required_approval=required_approval,
                assigned_team=assigned_team,
                source_policy=policy.get('id', 'Unknown'),
                status=status
            )
            ticket_id = ticket["ticket_id"]
            # Save the ticket
            self.ticket_generator.save_ticket(ticket)
        
        # Step 6: Audit log
        self.audit_logger.log_interaction(
            request_id=request_id,
            employee=employee,
            email=email,
            input_query=query,
            detected_intent=intent,
            retrieved_source=policy.get('id', 'Unknown'),
            decision=recommended_action,
            risk_level=risk_level,
            action_taken=f"Ticket created: {ticket_id}" if ticket_id else "No ticket created",
            ticket_id=ticket_id,
            final_response=response,
            reason=f"Based on policy {policy.get('id')} and risk assessment."
        )
        
        # Return the result
        result = {
            "request_id": request_id,
            "response": response,
            "intent": intent,
            "entities": entities,
            "policy_used": policy.get('id'),
            "policy_title": policy.get('title'),
            "risk_level": risk_level,
            "recommended_action": recommended_action,
            "ticket": ticket,
            "ticket_id": ticket_id
        }
        return result
    
    def _determine_required_approval(self, intent: str, entities: Dict[str, Any]) -> str:
        """Determine what approvals are required based on intent and entities."""
        if intent == "Laptop Replacement":
            laptop_years = entities.get('laptop_years', 0)
            if laptop_years < 4:
                return "Finance sign-off + IT approval"
            else:
                return "IT approval"
        elif intent == "VPN Access":
            if entities.get('employee_type') == 'contractor':
                return "manager approval"  # Changed to lowercase to match test
            else:
                return "none"  # Changed to lowercase
        elif intent == "Mailbox Quota":
            # Quota increase beyond 25GB requires manager approval
                return "manager approval"  # Changed to lowercase
        elif intent == "Home Office Equipment":
            return "manager sign-off + finance processing"  # Changed to lowercase
        elif intent == "Software Installation":
            # Non-catalog requires IT Security review (which is a form of approval)
                return "it security review"  # Changed to lowercase
        elif intent == "Access Request":
            return "security approval + business justification"  # Changed to lowercase
        else:
            return "none"

    def _determine_assigned_team(self, intent: str, entities: Dict[str, Any]) -> str:
        """Determine which team should handle the request."""
        if intent == "Security Incident":
            return "Security"
        elif intent == "VPN Access":
            return "IT"
        elif intent == "Password Reset":
            return "IT"
        elif intent == "Laptop Replacement" or intent == "Hardware Issue":
            return "IT"
        elif intent == "Software Installation":
            return "IT Security"
        elif intent == "Printer Issue":
            return "IT"
        elif intent == "Mailbox Quota":
            return "IT"
        elif intent == "Guest Wi-Fi":
            return "None (self-service)"
        elif intent == "Expense Tool":
            return "Finance (for access), IT (for technical issues)"
        elif intent == "Home Office Equipment":
            return "IT (shipping after approval)"
        elif intent == "Access Request":
            return "Security"
        else:
            return "IT"

# For testing
if __name__ == "__main__":
    router = AgentRouter()
    result = router.process_request(
        query="My laptop won’t turn on at all, it’s completely dead, had it about 3.5 years now.",
        request_id="REQ-01",
        employee="Aditi Sharma",
        email="aditi.sharma@veridian-corp.example"
    )
    print(result["response"])