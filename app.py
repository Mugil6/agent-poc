import streamlit as st

st.set_page_config(
    page_title="AIG Agentic Intake Portal",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Enterprise P&C Intake Portal")
st.markdown("### Agentic Orchestration Proof of Concept")

st.info(
    "**Architecture Overview:** This portal demonstrates a specialized multi-agent pipeline "
    "for automated P&C insurance ingestion. Select a dedicated agent node from the sidebar "
    "to test its capabilities."
)

st.markdown("""
### 🧠 The Agent Nodes
1. **🔍 ACORD Extractor (Node 1):** Parses highly structured, tabular P&C grid data from ACORD forms into strict JSON schemas for core system ingestion.
2. **🏢 Case Classifier (Node 2):** Reads the unstructured intent of broker submissions to dynamically classify payloads as bulk Bookrolls or standard New Business.

---
**Deployment Note:** This framework leverages open weights for rapid UI validation. 
In production, these exact modular nodes will be containerized and deployed as discrete AWS AgentCore functions within a secure VPC.
""")