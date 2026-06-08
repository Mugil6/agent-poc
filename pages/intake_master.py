import streamlit as st
import time
import json
import pandas as pd
from typing import List, Literal
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="Intake Master", layout="wide")
st.title("📥 Intake Workflow (Master Agent)")
st.markdown("### Orchestrating Nodes 1-4 Automatically")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.1-flash-lite") 

# SCHEMAS
class Address(BaseModel):
    street: str = Field(description="Street address or PO Box")
    city: str = Field(description="City")
    state: str = Field(description="State abbreviation")
    zip_code: str = Field(description="Zip or postal code")

class CompanyCoverage(BaseModel):
    company_letter: str = Field(description="Letter assigned to the company")
    company_name: str = Field(description="Name of the insurer")
    naic_code: str = Field(description="NAIC code")

class PolicyData(BaseModel):
    insurance_type: str = Field(description="Type of insurance")
    policy_number: str = Field(description="Policy number")
    effective_date: str = Field(description="Effective date")
    expiration_date: str = Field(description="Expiration date")

class CoverageLimit(BaseModel):
    limit_type: str = Field(description="Type of limit")
    limit_amount: str = Field(description="Dollar amount")

class ExtractorSchema(BaseModel):
    producer_name: str = Field(description="Full name of the producer")
    insured_name: str = Field(description="Name of the insured entity")
    insured_address: Address
    companies_affording_coverage: List[CompanyCoverage]
    policies: List[PolicyData]
    limits: List[CoverageLimit]

CaseType = Literal["BOOKROLL", "NEW_BUSINESS", "ESCALATE_TO_HUMAN"]
class ClassifierSchema(BaseModel):
    case_type: CaseType
    confidence_score: int
    detected_policy_count: str
    key_indicators: str
    detailed_reasoning: str

PriorityLevel = Literal["LOW", "MEDIUM", "HIGH", "URGENT"]
class CaseRecordSchema(BaseModel):
    client_name: str
    case_title: str
    priority: PriorityLevel
    assigned_queue: str
    executive_summary: str
    flagged_issues: str
    crm_payload: str

class ExceptionSchema(BaseModel):
    action_required: bool
    email_subject: str
    email_draft: str

#  MASTER ORCHESTRATION LOGIC
if "global_file_bytes" in st.session_state and st.session_state.global_file_bytes:
    st.image(st.session_state.global_file_bytes, caption="Active Payload", use_column_width=True)
    
    if st.button("🚀 Execute Autonomous Intake Workflow", type="primary", use_container_width=True):
        
        with st.status("Master Agent initializing...", expanded=True) as status:
            img_payload = {"mime_type": st.session_state.global_mime_type, "data": st.session_state.global_file_bytes}
            
            try:
                # SUB-AGENT 1
                status.update(label="Master Agent: Delegating to Extractor Node...")
                res1 = model.generate_content(
                    ["Extract ONLY the specific parameters defined in the schema (producer, insured details, companies, policies, and limits). Do NOT extract any other tabular data.", img_payload],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=ExtractorSchema)
                )
                st.session_state.n1_data = res1.text
                status.update(label="✅ Deep extraction complete.")
                time.sleep(4) 

                # SUB-AGENT 2
                status.update(label="Master Agent: Delegating to Intent Classifier...")
                res2 = model.generate_content(
                    ["Analyze document layout and explicitly explain the business intent (Bookroll vs New Business).", img_payload],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=ClassifierSchema)
                )
                st.session_state.n2_data = res2.text
                status.update(label="✅ Intent classified.")
                time.sleep(4)

                # SUB-AGENT 3 
                status.update(label="Master Agent: Synthesizing CRM Case Record...")
                res3 = model.generate_content(
                    [f"Create CRM record. Flag 'MISSING' data as high priority. \nNode 1: {res1.text} \nNode 2: {res2.text}"],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=CaseRecordSchema)
                )
                st.session_state.n3_data = res3.text
                status.update(label="✅ CRM payload synthesized.")
                time.sleep(4)

                # SUB-AGENT 4
                status.update(label="Master Agent: Checking for Exceptions...")
                res4 = model.generate_content(
                    [f"If 'flagged_issues' exist in this record: {res3.text}, draft a broker email requesting the missing docs. If clean, set action_required to false."],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=ExceptionSchema)
                )
                st.session_state.n4_data = res4.text
                
                status.update(label="Intake Workflow Complete!", state="complete", expanded=False)

            except Exception as e:
                status.update(label=f"Workflow Failed: {str(e)}", state="error")
                st.stop()

    # THE FINAL DASHBOARD 
    if st.session_state.get("n1_data") and st.session_state.get("n4_data"):
        st.success("🎉 Master Agent successfully orchestrated all Intake nodes.")
        st.divider()
        
        try:
            n1 = json.loads(st.session_state.n1_data)
            n2 = json.loads(st.session_state.n2_data)
            n3 = json.loads(st.session_state.n3_data)
            n4 = json.loads(st.session_state.n4_data)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Insured Entity", n1.get("insured_name", "Unknown"))
            c2.metric("Workflow Route", n2.get("case_type", "").replace("_", " "))
            c3.metric("System Priority", n3.get("priority", "Unknown"))
            
            with st.expander("🔍 View Deep Extraction Data (Node 1)", expanded=True):
                st.write(f"**Producer:** {n1.get('producer_name', 'Unknown')}")
                address = n1.get('insured_address', {})
                if address:
                    st.write(f"**Address:** {address.get('street', '')}, {address.get('city', '')}, {address.get('state', '')} {address.get('zip_code', '')}")
                
                st.markdown("##### Carrier Details")
                if n1.get('companies_affording_coverage'):
                    st.dataframe(pd.DataFrame(n1['companies_affording_coverage']), use_container_width=True)
                    
                st.markdown("##### Active Policies")
                if n1.get('policies'):
                    st.dataframe(pd.DataFrame(n1['policies']), use_container_width=True)
                    
                st.markdown("##### Liability Limits")
                if n1.get('limits'):
                    st.dataframe(pd.DataFrame(n1['limits']), use_container_width=True)

            with st.expander("🏢 View Classifier Reasoning (Node 2)", expanded=False):
                st.info(n2.get("detailed_reasoning", ""))
                st.warning(f"**Visual Clues:** {n2.get('key_indicators', '')}")

            if n4.get("action_required"):
                st.error(" Pipeline Halted: Exception Detected")
                st.warning(f"**Missing Data:** {n3.get('flagged_issues', '')}")
                st.markdown("##### Auto-Drafted Broker Communication (Node 4)")
                st.text_input("Subject", value=n4.get("email_subject", ""))
                st.text_area("To: Broker", value=n4.get("email_draft", ""), height=150)
            else:
                st.success("✨ Payload Clean. Ready for Assess Master Workflow.")
                
        except Exception as e:
            st.error(f"UI Rendering Error: {str(e)}")
            
else:
    st.warning(" No payload found. Please upload a document on the Home page.")