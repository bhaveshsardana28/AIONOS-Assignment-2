# Demo Script: Veridian IT Support Agent

## Target Length: 5-8 minutes

### 0:00–0:30 - Problem
[Opening screen: Show the Veridian IT Support Agent UI title]
Narrator: "In large organizations like Veridian Corp, IT support teams face a constant stream of employee requests. These requests vary widely in clarity, from simple questions like 'Can I get guest Wi-Fi?' to complex issues like security incidents or hardware failures. Employees need fast, accurate help, but IT teams must ensure every response follows company policy, assesses risk, and maintains proper documentation. Manual handling is slow and inconsistent. That's where our AI agent comes in."

### 0:30–1:15 - Architecture
[Show architecture diagram from architecture.md]
Narrator: "Our agent uses a hybrid architecture that combines the strengths of language models with deterministic policy enforcement. At the core is the agent router that orchestrates the flow: First, it uses natural language understanding to classify the employee's intent and extract key details like years of service or contractor status. Next, it retrieves the relevant policy from our knowledge base. Then, deterministic rules evaluate the request against that policy to assess risk and decide whether to resolve, clarify, or escalate. The agent generates a response grounded in the retrieved policy, creates a ticket if needed, and logs everything for audit. Crucially, the language model never makes authorization decisions—it only helps with understanding and response generation, with a fallback to rule-based methods if unavailable."

### 1:15–2:00 - Dashboard
[Show the Streamlit UI dashboard view]
Narrator: "Let's look at the dashboard. The sidebar shows the agent status, data source counts, and navigation. The main view displays key metrics: open requests, active tickets, resolved, escalated, and waiting for employee. Below that, we have our chat interface where employees can submit requests. We can also browse the employee requests, ticket queue, and audit logs from the sidebar."

### 2:00–3:00 - Demo 1: Guest Wi-Fi Request (Easy Resolution)
[Switch to chat interface]
Narrator: "First, let's try a simple request: 'Can I get Wi-Fi for a guest tomorrow?'"
[Type the request and hit enter]
Narrator: "The agent quickly responds: You can generate guest Wi-Fi credentials from the front-desk kiosk. The credentials will be valid for 24 hours. No IT ticket is required. Notice the source citation: KB-07 — Guest Wi-Fi Access. The agent correctly identified this as a low-risk request that requires no action from IT. No ticket was created, and the audit log shows a RESOLVE action with low risk. This demonstrates the agent's ability to provide instant, accurate self-service guidance."

### 3:00–4:00 - Demo 2: Phishing/Security Request (High-Risk Escalation)
[Clear chat or use new request]
Narrator: "Now, let's test a high-risk scenario: 'I got an email asking for my password. Is this legitimate?'"
[Type the request and hit enter]
Narrator: "The agent immediately identifies this as a security incident. The response is clear and urgent: Please immediately report any suspected phishing email to security@veridian-corp.example and do NOT forward it to other employees. The source is KB-09 — Security Incident Reporting. The risk is assessed as HIGH, and the action is ESCALATE. The agent created a ticket for the Security team, which we can see in the ticket queue. The audit log captures the full interaction, showing how the agent follows security protocol without hesitation."

### 4:00–5:00 - Demo 3: Laptop Replacement Request (Approval Workflow)
[New request]
Narrator: "Next, a more nuanced request: 'My laptop is dead and I've had it for 3.5 years.'"
[Type the request and hit enter]
Narrator: "The agent recognizes this involves two policies: KB-03 says laptops are eligible for replacement after 3 years or earlier with verified hardware failure. But the Asset Management Policy states that early replacement outside the 4-year cycle requires Finance sign-off and IT approval. The response explains: Your laptop is eligible for replacement but requires Finance sign-off and IT approval due to being less than 4 years old. The risk is MEDIUM, action is ESCALATE, and a ticket was created requiring those approvals. The agent didn't automatically approve replacement—it correctly identified the needed approvals, demonstrating conservative policy combination."

### 5:00–6:00 - Demo 4: Ambiguous Request (Clarification)
[New request]
Narrator: "Finally, an intentionally vague request: 'hey can you help, its not working'"
[Type the request and hit enter]
Narrator: "The agent does not guess. Instead, it asks for clarification: Sure — what isn't working? Please tell me the device/application/service and what error you're seeing. The risk is LOW, action is CLARIFY, and no ticket was created. This shows the agent's commitment to avoiding hallucination: when information is insufficient, it asks for clarification rather than making assumptions."

### 6:00–7:00 - Ticket + Audit Log
[Show ticket queue and audit logs]
Narrator: "Let's review what happened behind the scenes. In the ticket queue, we see the agent-generated tickets: one for the laptop replacement (AI-1002) requiring approvals, and one from the security incident (AI-1001). Each ticket contains all required details: request ID, employee, intent, risk level, recommended action, required approvals, assigned team, source policy, and timestamp. In the audit logs, we see a complete record of every interaction: timestamps, inputs, detected intents, policy sources, decisions, risk levels, actions taken, ticket IDs, final responses, and reasoning. This full audit trail ensures accountability and compliance."

### 7:00–8:00 - Architecture + Future Scope
[Show architecture diagram again]
Narrator: "To summarize, our agent provides policy-grounded, explainable, and safe IT support. It combines natural language flexibility with deterministic control to prevent hallucination and ensure compliance. The audit trail makes every action traceable. Looking ahead, with more time, we would enhance the system with embedding-based retrieval for better semantic understanding, integrate with enterprise ticketing and identity systems, add role-based access control, and implement human-in-the-loop workflows for complex approvals. But even in this lightweight implementation, we've demonstrated a working solution that strictly follows the supplied data, avoids invention, and provides real value to both employees and IT teams."

[Closing screen: Show contact/info]
Narrator: "Thank you for watching the Veridian IT Support Agent demo."