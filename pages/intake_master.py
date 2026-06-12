import streamlit as st
import time
import json
import pandas as pd
from typing import List, Literal
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="Intake Master", layout="wide")
st.title("📥 Intake Workflow (Agentic Node)")
st.markdown("### Orchestrating Nodes 1-4 with Granular Reasoning")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.1-flash-lite") 

# AGENTIC SCHEMAS (Added Scratchpads for Granularity)

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str

class CompanyCoverage(BaseModel):
    company_name: str
    naic_code: str

class PolicyData(BaseModel):
    insurance_type: str
    policy_number: str

class CoverageLimit(BaseModel):
    limit_type: str
    limit_amount: str

class ExtractorSchema(BaseModel):
    agent_scratchpad: str = Field(description="Step-by-step internal reasoning: 1. Locate Producer. 2. Scan for limits. 3. Validate NAIC codes format.")
    producer_name: str
    insured_name: str
    insured_address: Address
    companies_affording_coverage: List[CompanyCoverage]
    policies: List[PolicyData]
    limits: List[CoverageLimit]

class ClassifierSchema(BaseModel):
    agent_scratchpad: str = Field(description="Internal logic: What specific visual cues indicate this is a bookroll vs new business?")
    case_type: Literal["BOOKROLL", "NEW_BUSINESS", "ESCALATE_TO_HUMAN"]
    confidence_score: int
    key_indicators: str

class CaseRecordSchema(BaseModel):
    agent_scratchpad: str = Field(description="Evaluate missing data from previous nodes to determine CRM priority level.")
    client_name: str
    priority: Literal["LOW", "MEDIUM", "HIGH", "URGENT"]
    flagged_issues: str

class ExceptionSchema(BaseModel):
    action_required: bool
    email_draft: str

# MASTER ORCHESTRATION LOGIC

if "global_file_bytes" in st.session_state and st.session_state.global_file_bytes:
    
    if st.button("🚀 Execute Agentic Intake Workflow", type="primary", use_container_width=True):
        with st.status("Agent initializing...", expanded=True) as status:
            img_payload = {"mime_type": st.session_state.global_mime_type, "data": st.session_state.global_file_bytes}
            
            try:
                status.update(label="Agent reasoning through structural extraction...")
                res1 = model.generate_content(
                    ["Extract tabular data. Show your step-by-step reasoning in the agent_scratchpad.", img_payload],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=ExtractorSchema)
                )
                st.session_state.n1_data = res1.text
                time.sleep(4) 

                status.update(label="Agent analyzing business intent...")
                res2 = model.generate_content(
                    ["Analyze document layout for intent. Show reasoning in the agent_scratchpad.", img_payload],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=ClassifierSchema)
                )
                st.session_state.n2_data = res2.text
                time.sleep(4)

                status.update(label="Agent synthesizing CRM record...")
                res3 = model.generate_content(
                    [f"Create CRM record based on: {res1.text} and {res2.text}"],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=CaseRecordSchema)
                )
                st.session_state.n3_data = res3.text
                time.sleep(4)

                status.update(label="Agent checking for required exceptions...")
                res4 = model.generate_content(
                    [f"Draft broker exception email if issues exist here: {res3.text}"],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=ExceptionSchema)
                )
                st.session_state.n4_data = res4.text
                
                status.update(label="Agentic Intake Complete!", state="complete", expanded=False)

            except Exception as e:
                status.update(label=f"Workflow Failed: {str(e)}", state="error")
                st.stop()

    # DASHBOARD
    
    if st.session_state.get("n1_data") and st.session_state.get("n4_data"):
        st.success("🎉 Agent successfully reasoned through Intake nodes.")
        
        n1 = json.loads(st.session_state.n1_data)
        n2 = json.loads(st.session_state.n2_data)
        n3 = json.loads(st.session_state.n3_data)
        n4 = json.loads(st.session_state.n4_data)
        
        # Display the Agent's "Brain" to the stakeholders
        st.markdown("### 🧠 Agentic Reasoning Trace (Audit Log)")
        st.info(f"**Extraction Logic:** {n1.get('agent_scratchpad', 'N/A')}")
        st.info(f"**Classification Logic:** {n2.get('agent_scratchpad', 'N/A')}")
        st.divider()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Insured Entity", n1.get("insured_name", "Unknown"))
        c2.metric("Workflow Route", n2.get("case_type", ""))
        c3.metric("System Priority", n3.get("priority", ""))
        
        with st.expander("🔍 View Validated Tables", expanded=False):
            if n1.get('policies'): st.dataframe(pd.DataFrame(n1['policies']), use_container_width=True)
            if n1.get('limits'): st.dataframe(pd.DataFrame(n1['limits']), use_container_width=True)

        if n4.get("action_required"):
            st.error("⚠️ Exception Triggered.")
            st.text_area("To: Broker", value=n4.get("email_draft", ""), height=150)
else:
    st.warning("⚠️ No payload found.")