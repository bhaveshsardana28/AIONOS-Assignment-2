import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

class TicketGenerator:
    def __init__(self, tickets_path: str = "data/tickets.json"):
        self.tickets_path = tickets_path
        self.existing_tickets = self._load_tickets()
        # We'll generate IDs that are not in existing tickets
        # We'll use a prefix AI- and then a number
        # We'll find the max number in existing tickets that are like AI-XXXX? 
        # But existing tickets are TK-XXXX. We'll avoid TK- and use AI-.
        # We'll just use a UUID or timestamp for simplicity.
        # However, the example uses AI-XXXX. We'll generate a sequential number starting from 1000.
        # We'll keep a counter in a file or in memory. For simplicity, we'll use a timestamp-based ID.
        # But to avoid conflicts, we'll check existing tickets for AI- pattern.
        self.next_id = self._get_next_ticket_id()
    
    def _load_tickets(self) -> list:
        try:
            with open(self.tickets_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _get_next_ticket_id(self) -> int:
        # Look for existing AI- tickets in our in-memory list? We don't store them yet.
        # We'll just start from 1000 and assume no conflict.
        # In a real system, we'd query a database.
        return 1000
    
    def generate_ticket_id(self) -> str:
        ticket_id = f"AI-{self.next_id}"
        self.next_id += 1
        return ticket_id
    
    def create_ticket(self, 
                     request_id: str,
                     employee: str,
                     email: str,
                     intent: str,
                     issue_summary: str,
                     risk_level: str,
                     recommended_action: str,
                     required_approval: str,
                     assigned_team: str,
                     source_policy: str,
                     status: str = "Open") -> Dict[str, Any]:
        """
        Create a structured ticket.
        """
        ticket = {
            "ticket_id": self.generate_ticket_id(),
            "request_id": request_id,
            "employee": employee,
            "email": email,
            "intent": intent,
            "issue_summary": issue_summary,
            "risk_level": risk_level,
            "recommended_action": recommended_action,
            "required_approval": required_approval,
            "assigned_team": assigned_team,
            "status": status,
            "source_policy": source_policy,
            "created_at": datetime.now().isoformat(),
            "reason": f"Based on policy {source_policy} and risk assessment."
        }
        return ticket
    
    def save_ticket(self, ticket: Dict[str, Any]):
        """
        Save the ticket to the tickets file.
        For simplicity, we'll append to the list and write back.
        In a real system, we'd have a proper database.
        """
        self.existing_tickets.append(ticket)
        with open(self.tickets_path, 'w') as f:
            json.dump(self.existing_tickets, f, indent=2)

# For testing
if __name__ == "__main__":
    generator = TicketGenerator()
    ticket = generator.create_ticket(
        request_id="REQ-01",
        employee="Aditi Sharma",
        email="aditi.sharma@veridian-corp.example",
        intent="Laptop Replacement",
        issue_summary="Laptop dead after 3.5 years",
        risk_level="MEDIUM",
        recommended_action="ESCALATE",
        required_approval="Finance sign-off + IT approval",
        assigned_team="IT",
        source_policy="KB-03, Asset Management Policy",
        status="Open"
    )
    print(ticket)