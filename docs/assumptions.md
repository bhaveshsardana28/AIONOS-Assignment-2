# Assumptions

This document outlines the assumptions made during the development of the Veridian IT Support Agent.

## Data Assumptions

1. **Knowledge Base Completeness**
   - The supplied policies (KB-01 through KB-10 and Asset Management Policy) are sufficient to handle all employee requests
   - No additional policies or procedures exist outside of what was provided
   - Policies are correct, up-to-date, and non-contradictory

2. **Employee Request Data**
   - The 15 sample employee requests are representative of common IT issues
   - Dates are in a format that does not affect logic (treated as strings)
   - Email addresses follow the veridian-corp.example domain
   - Initial action fields are for context only and not used in decision making

3. **Existing Ticket Queue**
   - The 10 sample tickets are historical records that provide context but do not establish new policy
   - Ticket statuses accurately reflect their current state
   - Ticket issues are concise summaries of the problems
   - Resolved/Rejected/Closed tickets should not be treated as precedent for new policy

## Technical Assumptions

1. **Language Model**
   - If an OpenAI API key is provided, the model gpt-3.5-turbo is available and functional
   - The LLM understands and follows instructions to ground responses in supplied evidence
   - When LLM is unavailable, deterministic fallback methods provide equivalent functionality in terms of decision making (though responses may be less natural)

2. **Retrieval System**
   - Simple keyword-based retrieval (Jaccard similarity) is sufficient for this small, well-defined knowledge base
   - Policies are sufficiently distinct that the highest similarity match is usually correct
   - No policy requires complex semantic understanding to retrieve

3. **Deterministic Rules**
   - The policy rules as interpreted from the supplied documents are complete and correct
   - Edge cases not explicitly covered in the policies can be handled through clarification or escalation
   - The combination of multiple policies (e.g., KB-03 and Asset Management Policy) follows a conservative interpretation

4. **Ticketing System**
   - The ticket ID generation scheme (AI-XXXX) will not conflict with existing TK-XXXX tickets
   - The volume of tickets generated does not require high-performance storage
   - Simple JSON file storage is adequate for demonstration and testing

5. **Audit Logging**
   - Audit logs are write-once and do not require real-time querying
   - The JSON format is sufficient for audit trail purposes
   - Log size will remain manageable for the scope of this assignment

## Business Assumptions

1. **Employee Roles**
   - Employees are full-time unless explicitly identified as contractors
   - Contractor status affects VPN access and certain approval processes
   - Manager approval refers to the employee's direct manager

2. **IT Department Scope**
   - IT handles password resets, VPN access, hardware issues, software installation (technical aspect), printer issues, mailbox quotas, guest Wi-Fi setup, and security incident routing
   - IT does not handle expense tool access approval (Finance domain) or security incident investigation (Security domain)
   - IT assists with technical aspects of expense tool login only after access is granted by Finance

3. **Approval Processes**
   - Manager approval means a formal approval process exists (e.g., form, email approval)
   - Finance processing refers to the standard financial workflow for purchases and allowances
   - IT Security review takes 3-5 business days as stated in KB-04
   - Approvals are binary (granted/denied) and not subject to nuanced conditions in this model

4. **Escalation Paths**
   - Security incidents go to the Security team via email to security@veridian-corp.example
   - Approval-dependent requests are escalated for managerial or financial review
   - Other escalations go to appropriate IT sub-teams (IT Security, IT Hardware, etc.)

5. **Self-Service Capabilities**
   - Employees can reset passwords via self-service portal at any time
   - Employees can generate guest Wi-Fi credentials from front-desk kiosk
   - Standard software in approved catalog can be self-installed without IT involvement

## Limitations of Assumptions

These assumptions simplify the problem scope for the assignment but may not hold in a real-world enterprise:

- Real enterprises have more complex, evolving policies that may conflict
- Employee roles and approval hierarchies are more nuanced
- Integration with existing IT service management (ITSM) tools is necessary
- Audit requirements may be more stringent (e.g., tamper-proof logs)
- Language model use may be restricted in certain environments
- The system assumes good faith users; malicious input handling is minimal

## Validation of Assumptions

Where possible, assumptions were validated against the supplied data:

- Policy interpretations were based solely on the provided text
- Employee request handling followed the patterns in the sample data
- Ticket usage respected the distinction between active and historical tickets
- Risk levels were assigned conservatively to avoid under-escalation