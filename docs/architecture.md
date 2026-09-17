# System Architecture

## Overview

The Veridian IT Support Agent follows a modular architecture that separates concerns between the user interface, agent orchestration, natural language processing, policy retrieval, deterministic reasoning, and side effects (ticketing, audit).

## Components

### 1. Streamlit UI (`app.py`)
- Responsible for rendering the user interface
- Handles user input and displays agent responses
- Provides navigation between different views (Chat, Employee Requests, Ticket Queue, Audit Logs)
- Manages session state for interaction history

### 2. Agent Router (`agent/router.py`)
- Orchestrates the end-to-end request processing pipeline
- Coordinates between LLM handler, policy engine, ticket generator, and audit logger
- Determines when to create tickets based on intent and policy
- Manages fallback mechanisms when LLM is unavailable

### 3. LLM Handler (`agent/llm_handler.py`)
- Provides integration with large language models (OpenAI GPT-3.5-Turbo)
- Implements fallback to rule-based methods when LLM is unavailable
- Handles:
  - Intent classification and entity extraction
  - Natural language response generation
- All LLM calls are grounded with retrieved policy context

### 4. Policy Engine (`agent/policy_engine.py`)
- Contains deterministic logic for:
  - Intent classification (rule-based fallback)
  - Entity extraction (rule-based)
  - Policy evaluation against extracted entities
  - Risk assessment based on intent and entities
  - Determination of required approvals and assigned teams
- Does not make final decisions independently; provides inputs to the router

### 5. Retrieval (`agent/retrieval.py`)
- Loads and searches the policy knowledge base
- Uses simple keyword matching (Jaccard similarity) to find relevant policies
- Returns the most relevant policy along with a confidence score
- Knowledge base is stored in `data/policies.json`

### 6. Ticket Generator (`agent/ticketing.py`)
- Creates structured ticket objects when required
- Generates unique ticket IDs (AI-XXXX format)
- Saves tickets to the persistent ticket store (`data/tickets.json`)
- Includes all required ticket metadata (request ID, employee, intent, risk, etc.)

### 7. Audit Logger (`agent/audit.py`)
- Records every agent interaction for compliance and review
- Stores audit logs in `data/audit_log.json`
- Captures timestamp, request details, intent, policy source, decision, risk, action, ticket ID, and response

## Data Flow

1. User submits a request through the Streamlit UI
2. Router receives the request and optional context (request ID, employee, email)
3. Router calls LLM Handler to classify intent and extract entities (with fallback)
4. Router uses Retriever to find the most relevant policy
5. Router calls Policy Engine to assess risk and determine recommended action
6. Router calls LLM Handler to generate a natural language response (with fallback)
7. If action requires a ticket, Router calls Ticket Generator to create and save ticket
8. Router calls Audit Logger to record the interaction
9. Router returns the response and metadata to the UI for display

## Security Considerations

- No direct LLM access to make authorization decisions; all decisions flow through deterministic policy engine
- All LLM prompts include instructions to ground responses in supplied evidence only
- Risk assessment prevents automatic approval of high-risk requests
- Audit trail ensures traceability of all agent actions
- Knowledge base is read-only and confined to supplied data

## Scalability

- Current implementation uses JSON files for simplicity
- For production, JSON stores could be replaced with a relational database or document store
- Agent router is stateless and could be horizontally scaled
- LLM handler could be adapted to use different providers or local models