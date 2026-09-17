import streamlit as st
import json
import os
from agent.router import AgentRouter

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Veridian IT Support Agent",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the agent router
@st.cache_resource
def get_router():
    return AgentRouter()

router = get_router()

# Load data for display
@st.cache_data
def load_data():
    data_dir = "data"
    policies = json.load(open(os.path.join(data_dir, "policies.json")))
    employee_requests = json.load(open(os.path.join(data_dir, "employee_requests.json")))
    tickets = json.load(open(os.path.join(data_dir, "tickets.json")))
    return policies, employee_requests, tickets

policies, employee_requests, tickets = load_data()

# Sidebar
with st.sidebar:
    st.title("Veridian IT Support")
    st.subheader("Agent Status")
    st.success("Agent Online")
    
    st.subheader("Data Source Status")
    st.info(f"Policies Loaded: {len(policies)}")
    st.info(f"Employee Requests Loaded: {len(employee_requests)}")
    st.info(f"Existing Tickets: {len(tickets)}")
    
    st.subheader("Navigation")
    page = st.radio("Go to", ["Chat Interface", "Employee Requests", "Ticket Queue", "Audit Logs"])
    
    st.subheader("New Request")
    new_request_text = st.text_area("Describe your IT issue:", height=100)
    if st.button("Submit Request"):
        if new_request_text.strip():
            # Process the new request
            with st.spinner("Processing your request..."):
                result = router.process_request(
                    query=new_request_text,
                    employee="Current User",  # In a real app, we'd get this from auth
                    email="user@veridian-corp.example"
                )
                st.session_state.last_result = result
                st.rerun()
        else:
            st.warning("Please enter a request.")

# Main content
st.title("Veridian IT Support Agent")
st.caption("AI-powered employee IT support and intelligent escalation")

if page == "Chat Interface":
    st.header("Chat with IT Support Agent")
    
    # Display last result if exists
    if 'last_result' in st.session_state:
        result = st.session_state.last_result
        
        st.subheader("Agent Response")
        st.write(result['response'])
        
        # Show source
        with st.expander("View Source Policy"):
            st.write(f"**{result['policy_used']} - {result['policy_title']}**")
            # We don't have the full content here, but we could fetch it
            # For now, we'll just show the ID and title
        
        # Show metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Intent", result['intent'])
        with col2:
            st.metric("Risk Level", result['risk_level'])
        with col3:
            st.metric("Action", result['recommended_action'])
        with col4:
            if result['ticket_id']:
                st.metric("Ticket ID", result['ticket_id'])
            else:
                st.metric("Ticket ID", "None")
        
        # Show ticket if created
        if result['ticket']:
            st.subheader("Generated Ticket")
            st.json(result['ticket'])
    
    # Example requests from the data
    st.subheader("Try an Example Request")
    example_options = [f"{req['id']}: {req['request']}" for req in employee_requests]
    selected_example = st.selectbox("Select an example request:", [""] + example_options)
    if selected_example and st.button("Load Example"):
        # Extract the request text
        req_id = selected_example.split(":")[0]
        req_text = next(req['request'] for req in employee_requests if req['id'] == req_id)
        st.session_state.example_query = req_text
        st.rerun()
    
    if 'example_query' in st.session_state:
        st.info(f"Example query: {st.session_state.example_query}")
        if st.button("Process Example"):
            with st.spinner("Processing..."):
                # Find the employee info for this request
                req_obj = next(req for req in employee_requests if req['request'] == st.session_state.example_query)
                result = router.process_request(
                    query=st.session_state.example_query,
                    request_id=req_obj['id'],
                    employee=req_obj['employee'],
                    email=req_obj['email']
                )
                st.session_state.last_result = result
                # Clear the example query
                del st.session_state.example_query
                st.rerun()

elif page == "Employee Requests":
    st.header("Employee Requests")
    st.dataframe(
        [
            {
                "ID": req["id"],
                "Employee": req["employee"],
                "Email": req["email"],
                "Date": req["date"],
                "Request": req["request"],
                "Initial Action": req["initial_action"]
            }
            for req in employee_requests
        ],
        use_container_width=True
    )

elif page == "Ticket Queue":
    st.header("Ticket Queue")
    # Separate active and historical tickets
    active_tickets = [t for t in tickets if t["status"] not in ["Resolved (closed)", "Rejected (closed)", "Approved (closed)"]]
    historical_tickets = [t for t in tickets if t["status"] in ["Resolved (closed)", "Rejected (closed)", "Approved (closed)"]]
    
    st.subheader("Active Tickets")
    if active_tickets:
        st.dataframe(
            [
                {
                    "ID": t.get("ticket_id", t.get("id", "Unknown")),
                    "Employee": t["employee"],
                    "Issue": t.get("issue_summary", t.get("issue", "Unknown")),
                    "Status": t.get("status", "Unknown")
                }
                for t in active_tickets
            ],
            use_container_width=True
        )
    else:
        st.info("No active tickets.")
    
    st.subheader("Historical Tickets")
    if historical_tickets:
        st.dataframe(
            [
                {
                    "ID": t.get("ticket_id", t.get("id", "Unknown")),
                    "Employee": t["employee"],
                    "Issue": t.get("issue_summary", t.get("issue", "Unknown")),
                    "Status": t.get("status", "Unknown")
                }
                for t in historical_tickets
            ],
            use_container_width=True
        )
    else:
        st.info("No historical tickets.")
    
    # Also show any tickets generated by the agent
    # We would need to load the updated tickets.json that includes AI- tickets
    # For simplicity, we'll note that the ticketing module saves to the same file.
    # So we can just show all tickets and note the AI- ones.
    ai_tickets = [t for t in tickets if t.get("ticket_id", t.get("id", "")).startswith("AI-")]
    if ai_tickets:
        st.subheader("Agent-Generated Tickets")
        st.dataframe(
            [
                {
                    "ID": t.get("ticket_id", t.get("id", "Unknown")),
                    "Request ID": t.get("request_id", "Unknown"),
                    "Employee": t["employee"],
                    "Intent": t.get("intent", "Unknown"),
                    "Status": t.get("status", "Unknown")
                }
                for t in ai_tickets
            ],
            use_container_width=True
        )

elif page == "Audit Logs":
    st.header("Audit Logs")
    # Load audit log from the audit logger
    audit_logger = router.audit_logger
    audit_log = audit_logger.get_audit_log()
    if audit_log:
        # Display in reverse chronological order (newest first)
        for entry in reversed(audit_log):
            with st.expander(f"{entry['timestamp']} - {entry['request_id']} - {entry['detected_intent']}"):
                st.json(entry)
    else:
        st.info("No audit logs yet.")

# Footer
st.divider()
st.caption("Veridian IT Support Agent • Built for AIONOS Assignment 2")