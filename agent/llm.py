import os
from typing import Dict, Any, Tuple, Optional
import json

class LLMHandler:
    def __init__(self):
        self.use_llm = False
        self.model = None
        # Try to load OpenAI API key if available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                import openai
                openai.api_key = api_key
                self.use_llm = True
                self.model = "gpt-3.5-turbo"
            except ImportError:
                pass
    
    def classify_intent_and_extract_entities(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """
        Use LLM to classify intent and extract entities.
        Fallback to rule-based if LLM not available.
        """
        if self.use_llm:
            try:
                return self._llm_classify_and_extract(query)
            except Exception as e:
                print(f"LLM error: {e}. Falling back to rule-based.")
                return self._fallback_classify_and_extract(query)
        else:
            return self._fallback_classify_and_extract(query)
    
    def _llm_classify_and_extract(self, query: str) -> Tuple[str, Dict[str, Any]]:
        # This is a simplified version. In practice, we would use a fine-tuned model or careful prompting.
        # For demonstration, we'll use a basic prompt.
        prompt = f"""
        Given the following employee IT support query, classify the intent and extract relevant entities.
        Intent categories: Password Reset, VPN Access, Laptop Replacement, Hardware Issue, Software Installation, Printer Issue, Mailbox Quota, Guest Wi-Fi, Expense Tool, Security Incident, Home Office Equipment, Access Request, Unknown / Ambiguous.
        
        Entities to extract if present:
        - laptop_years: number of years the employee has had the laptop
        - employee_type: either 'full-time' or 'contractor'
        - hardware_failure_indicated: boolean if the query indicates verified hardware failure
        - password_attempts: number of failed password attempts
        - wfh_days_per_week: number of days per week working from home
        - vpn_expired: boolean if VPN credentials are mentioned as expired
        - mailbox_full: boolean if mailbox is full
        - phishing_suspected: boolean if phishing is suspected
        - asset_tag_requested: boolean if asset tag is mentioned
        - expense_tool_issue: boolean if expense tool login issue
        - admin_access_request: boolean if admin access is requested
        
        Query: "{query}"
        
        Respond in JSON format:
        {{
          "intent": "...",
          "entities": {{
            "laptop_years": null or number,
            "employee_type": null or string,
            ... (other entities)
          }}
        }}
        """
        import openai
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an IT support assistant that classifies intents and extracts entities."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        result = json.loads(response.choices[0].message['content'])
        intent = result['intent']
        entities = result['entities']
        # Clean null values
        entities = {k: v for k, v in entities.items() if v is not None}
        return intent, entities
    
    def _fallback_classify_and_extract(self, query: str) -> Tuple[str, Dict[str, Any]]:
        # Use the same logic as in policy_engine for fallback
        from .policy_engine import PolicyEngine
        engine = PolicyEngine()
        entities = engine.extract_entities(query)
        intent = engine._determine_intent(query, {}, entities)  # We pass empty policy, but the method doesn't really use it for intent?
        # Actually, the _determine_intent method uses query and entities, not policy.
        # So we can call it with empty policy.
        return intent, entities
    
    def generate_explanation(self, 
                           query: str, 
                           intent: str, 
                           policy: Dict[str, Any], 
                           risk_level: str, 
                           decision: str,
                           entities: Dict[str, Any]) -> str:
        """
        Generate a natural language explanation based on the policy and decision.
        Fallback to template-based if LLM not available.
        """
        if self.use_llm:
            try:
                return self._llm_generate_explanation(query, intent, policy, risk_level, decision, entities)
            except Exception as e:
                print(f"LLM error in explanation: {e}. Falling back to template.")
                return self._template_explanation(query, intent, policy, risk_level, decision, entities)
        else:
            return self._template_explanation(query, intent, policy, risk_level, decision, entities)
    
    def _llm_generate_explanation(self, query: str, intent: str, policy: Dict[str, Any], risk_level: str, decision: str, entities: Dict[str, Any]) -> str:
        prompt = f"""
        You are an IT support agent. Based on the user query, the identified intent, the relevant policy, the risk level, and the decision, generate a helpful response to the employee.
        Follow these guidelines:
        - Answer only from the supplied evidence (the policy).
        - If evidence is insufficient, say so and ask a clarification question or escalate.
        - Never invent company policy.
        - Include the source of the policy in the response.
        - Be concise and professional.
        
        User Query: {query}
        Intent: {intent}
        Policy: {policy['content']}
        Risk Level: {risk_level}
        Decision: {decision}
        Entities: {json.dumps(entities)}
        
        Generate the response:
        """
        import openai
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an IT support agent that provides policy-grounded responses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        return response.choices[0].message['content'].strip()
    
    def _template_explanation(self, query: str, intent: str, policy: Dict[str, Any], risk_level: str, decision: str, entities: Dict[str, Any]) -> str:
        # Template-based response generation
        policy_title = policy.get('title', 'Unknown Policy')
        policy_id = policy.get('id', 'Unknown')
        policy_content = policy.get('content', '')
        
        # Start with a base response
        if decision == "RESOLVE":
            response = f"Based on the policy ({policy_id} - {policy_title}):\n\n{policy_content}\n\n"
            # Add specific guidance based on intent
            if intent == "Guest Wi-Fi":
                response += "You can generate guest Wi-Fi credentials from the front-desk kiosk. The credentials will be valid for 24 hours. No IT ticket is required."
            elif intent == "Mailbox Quota":
                response += "Your mailbox quota is 25GB. Please archive old mail to free up space. If you need a quota increase beyond 25GB (up to 50GB), you will need manager approval."
            elif intent == "Password Reset" and entities.get('password_attempts', 0) < 5:
                response += "You can reset your password via the self-service portal at any time."
            # Add more as needed
            else:
                response += "Please follow the guidelines outlined in the policy."
        
        elif decision == "ESCALATE":
            response = f"I've analyzed your request and it requires escalation. Here's why:\n\n"
            response += f"Policy: {policy_id} - {policy_title}\n{policy_content}\n\n"
            if risk_level == "HIGH":
                response += "This is a HIGH risk request. "
            elif risk_level == "MEDIUM":
                response += "This request requires approval or action from another team. "
            response += "I have escalated this for further review."
            # Add specific guidance
            if intent == "Security Incident":
                response += " Please immediately report any suspected phishing email to security@veridian-corp.example and do NOT forward it to other employees."
            elif intent == "VPN Access" and entities.get('employee_type') == 'contractor':
                response += " As a contractor, you need manager approval via the access request form."
            elif intent == "Laptop Replacement":
                response += " Your laptop is eligible for replacement, but because it is less than 4 years old, early replacement requires Finance sign-off and IT approval."
            elif intent == "Home Office Equipment":
                response += " You are eligible for home office equipment, but this requires manager sign-off and Finance processing. IT handles shipping only after approval."
            elif intent == "Access Request":
                response += " Admin access requests require careful review and justification."
        
        elif decision == "CLARIFY":
            response = "I need a bit more information to help you properly.\n\n"
            # Add specific clarification questions based on intent
            if intent == "Laptop Replacement":
                response += "How long have you had the laptop? Is there a verified hardware failure? Is this a replacement request or a repair issue?"
            elif intent == "Hardware Issue":
                response += "Let's troubleshooting: have you tried restarting the device? If the issue persists, please describe the problem."
            elif intent == "VPN Access":
                response += "Are you a full-time employee or a contractor?"
            elif intent == "Software Installation":
                response += "Is the software you wish to install in the approved catalog?"
            elif intent == "Printer Issue":
                response += "Have you checked the printer queue and restart the print spooler?"
            elif intent == "Expense Tool":
                response += "Do you already have an account with the expense management tool?"
            elif intent == "Unknown / Ambiguous":
                response += "Could you please clarify what isn't working? Please tell me the device/application/service and what error you're seeing."
            else:
                response += "Could you please provide more details about your issue?"
        
        # Add source citation
        response += f"\n\nSource: {policy_id} — {policy_title}"
        return response

# For testing
if __name__ == "__main__":
    handler = LLMHandler()
    # Test fallback
    query = "My laptop won’t turn on at all, it’s completely dead, had it about 3.5 years now."
    intent, entities = handler.classify_intent_and_extract_entities(query)
    print(f"Intent: {intent}")
    print(f"Entities: {entities}")
    
    # Dummy policy
    policy = {
        "id": "KB-03",
        "title": "Laptop Replacement",
        "content": "Laptops are eligible for replacement after 3 years of service, or earlier in case of verified hardware failure.\nRequests must be raised at least 2 weeks in advance of intended replacement."
    }
    explanation = handler.generate_explanation(query, intent, policy, "MEDIUM", "ESCALATE", entities)
    print(f"Explanation: {explanation}")