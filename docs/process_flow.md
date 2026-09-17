# Agent Process Flow

## Detailed Steps

This document describes the detailed flow of processing an employee IT support request from input to response.

### Step 0: Preconditions
- Knowledge base (policies.json) is loaded
- Employee requests and existing tickets are loaded for context
- Agent router is initialized with all subcomponents

### Step 1: Request Intake
**Location**: `app.py` → `AgentRouter.process_request()`
- User submits text query via chat interface or selects an example
- Optional metadata: request_id, employee name, email
- If metadata missing, placeholders are generated for new requests

### Step 2: Intent Classification & Entity Extraction
**Location**: `llm_handler.classify_intent_and_extract_entities()`
- Attempts to use LLM (OpenAI) if API key available
- Falls back to rule-based method in `policy_engine.extract_entities()` and `_determine_intent()`
- Returns:
  - `intent`: One of 13 predefined categories
  - `entities`: Dictionary of extracted values (laptop_years, employee_type, etc.)

### Step 3: Policy Retrieval
**Location**: `retrieval.PolicyRetriever.retrieve()`
- Loads policies from `data/policies.json`
- Computes similarity between query and each policy using Jaccard index on token sets
- Returns the policy with highest similarity score and the score itself
- If no similarity found, returns first policy with zero confidence

### Step 4: Risk Assessment & Decision Making
**Location**: `policy_engine._apply_rules()` (called via router)
- Takes intent, entities, and retrieved policy as input
- Applies deterministic rules specific to each intent
- Returns:
  - `risk_level`: LOW, MEDIUM, or HIGH
  - `recommended_action`: RESOLVE, CLARIFY, or ESCALATE

### Step 5: Response Generation
**Location**: `llm_handler.generate_explanation()`
- Attempts to use LLM to generate natural language explanation
- Falls back to template-based method in `llm_handler._template_explanation()`
- Inputs:
  - Original query
  - Classified intent
  - Retrieved policy
  - Risk level
  - Recommended action
  - Extracted entities
- Output: User-friendly response that cites the policy source

### Step 6: Ticket Creation (Conditional)
**Location**: `ticketing.TicketGenerator.create_ticket()` (called via router)
- Triggered when:
  - Recommended action is ESCALATE (always)
  - Recommended action is RESOLVE AND policy contains ticket-related language (e.g., "log a ticket")
- Creates structured ticket with:
  - Unique ID (AI-XXXX format)
  - Request ID, employee, email
  - Intent, issue summary (truncated query)
  - Risk level and recommended action
  - Required approvals and assigned team (determined by helper methods)
  - Source policy ID
  - Timestamp and status ("Open")
- Saves ticket to `data/tickets.json`

### Step 7: Audit Logging
**Location**: `audit.AuditLogger.log_interaction()` (called via router)
- Creates audit record with:
  - Timestamp
  - Request ID, employee, email
  - Original query
  - Detected intent
  - Retrieved policy source (ID)
  - Decision (action)
  - Risk level
  - Action taken (ticket ID or "No ticket created")
  - Final response
  - Reason (policy basis)
- Appends to `data/audit_log.json`

### Step 8: Response Return
**Location**: `app.py` (chat interface)
- Displays agent response to user
- Shows expander with source policy information
- Displays metrics (intent, risk, action, ticket ID)
- If ticket was created, shows ticket details in JSON format

## Decision Points

### Intent Classification
- Uses hybrid LLM/rule-based approach
- Fallback ensures functionality without LLM
- Intent categories are mutually exclusive and exhaustive

### Policy Retrieval
- Simple similarity metric suitable for small, distinct knowledge base
- Confidence score informs but does not block processing
- Low confidence triggers more cautious responses in templates

### Risk Assessment
- Deterministic rules prevent unwanted automation
- HIGH risk always leads to escalation
- MEDIUM risk leads to escalation when approvals are needed
- LOW risk allows resolution or clarification

### Action Selection
- RESOLVE: Policy explicitly permits self-service or informational response
- CLARIFY: Required information missing to make determination
- ESCALATE: Request requires human judgment, approvals, or is high-risk

### Ticket Creation
- Not all actions require tickets (e.g., pure information, clarification)
- Tickets created for traceability when action is taken or escalation occurs
- Avoids ticket overload for routine informational requests

## Error Handling

- LLM failures trigger fallback to deterministic methods
- Missing data defaults to safe values (e.g., unknown employee)
- Policy retrieval always returns a policy (fallback to first)
- All external file operations include error handling for missing files
- Validation ensures required ticket fields are present

## Example Flow: Guest Wi-Fi Request

1. **Query**: "Can I get Wi-Fi for a guest tomorrow?"
2. **Intent**: Guest Wi-Fi (matched via keyword)
3. **Entities**: {} (no specific entities extracted)
4. **Policy**: KB-07 - Guest Wi-Fi Access (highest similarity)
5. **Risk**: LOW (per policy: no IT ticket required)
6. **Action**: RESOLVE
7. **Response**: Template explains guest Wi-Fi process, cites KB-07
8. **Ticket**: None (policy says no IT ticket required)
9. **Audit**: Logged with decision RESOLVE, risk LOW

## Example Flow: Phishing Email

1. **Query**: "I think I got a phishing email asking for my login"
2. **Intent**: Security Incident (keyword match)
3. **Entities**: {phishing_suspected: True}
4. **Policy**: KB-09 - Security Incident Reporting
5. **Risk**: HIGH (explicit in rules)
6. **Action**: ESCALATE
7. **Response**: Template directs to security@veridian-corp.example, warns not to forward
8. **Ticket**: Created for Security team
9. **Audit**: Logged with decision ESCALATE, risk HIGH

## Extensibility

- New intents can be added by updating:
  - Intent classification rules in `_determine_intent()`
  - Risk and action rules in `_apply_rules()`
  - Template responses in `_template_explanation()`
  - Helper methods for approvals and teams
- New policies can be added to `data/policies.json`
- Retrieval automatically picks up new policies
- UI requires no code changes for new intents (they appear in metrics)