import streamlit as st
import os
import json
from typing import List, Literal
from pydantic import BaseModel, Field
import google.generativeai as genai


# 1. UI CONFIGURATION

st.set_page_config(page_title="Case Creation Agent", layout="wide")
st.title("📝 Automated Case Creation Agent")
st.markdown("### Multi-Agent Pipeline: Node 3 (System Integration)")

# 2. SECURE API KEY HANDLING

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    os.environ["GEMINI_API_KEY"] = api_key
    genai.configure(api_key=api_key)
except KeyError:
    st.error("⚠️ **Setup Error:** GEMINI_API_KEY not found in secrets.")
    st.stop()

# 3. UNDER THE HOOD SCHEMAS (Node 1 & Node 2 Models)

class Address(BaseModel):
    street: str = Field(description="Street address or PO Box")
    city: str = Field(description="City")
    state: str = Field(description="State abbreviation")
    zip_code: str = Field(description="Zip or postal code. Output 'MISSING' if not present.")

class CompanyCoverage(BaseModel):
    company_letter: str = Field(description="Letter assigned to the company (e.g., A, B, C)")
    company_name: str = Field(description="Name of the insurer")
    naic_code: str = Field(description="NAIC code. Output 'MISSING' if not present.")

class PolicyData(BaseModel):
    insurance_type: str = Field(description="Type of insurance")
    policy_number: str = Field(description="Policy number")
    effective_date: str = Field(description="Effective date (MM/DD/YYYY)")
    expiration_date: str = Field(description="Expiration date (MM/DD/YYYY)")
    tenure: str = Field(description="Calculated tenure of the policy. Output 'MISSING' if not present.")

class CoverageLimit(BaseModel):
    limit_type: str = Field(description="Type of limit")
    limit_amount: str = Field(description="Dollar amount of the limit")

class ExtractedDataSchema(BaseModel):
    producer_name: str = Field(description="Full name of the producer/agency")
    insured_name: str = Field(description="Name of the insured entity")
    insured_address: Address = Field(description="Split address components")
    insured_contact: str = Field(description="Contact details. Output 'MISSING' if not present.")
    companies_affording_coverage: List[CompanyCoverage] = Field(description="List of companies affording coverage")
    policies: List[PolicyData] = Field(description="List of policies")
    limits: List[CoverageLimit] = Field(description="List of coverage limits")

CaseType = Literal["BOOKROLL", "NEW_BUSINESS", "ESCALATE_TO_HUMAN"]

class IntentSchema(BaseModel):
    case_type: CaseType = Field(description="Classify as BOOKROLL (bulk transfer of policies) or NEW_BUSINESS (single/few new policies).")
    confidence_score: int = Field(description="Confidence score of the classification from 1 to 100.")

# 4. NODE 3 SCHEMA (The Final Output Ticket)

PriorityLevel = Literal["LOW", "MEDIUM", "HIGH", "URGENT"]

class CaseRecord(BaseModel):
    case_title: str = Field(description="A short, standardized title for the case (e.g., 'New Business Submission - Acme Corp').")
    priority: PriorityLevel = Field(description="Determine SLA priority based on intent and missing data.")
    assigned_queue: str = Field(description="The specific operational team this should be routed to (e.g., 'Bulk Processing Team', 'Standard Review Team', 'Exceptions Desk').")
    executive_summary: str = Field(description="A 2-3 sentence summary of the case for the human reviewer to read immediately upon opening the ticket.")
    flagged_issues: str = Field(description="List any missing fields or anomalies that the human must address. Output 'None' if perfectly clean.")
    crm_payload: str = Field(description="A stringified JSON object representing the final payload to be pushed via API to the core system.")


# 5. INITIALIZE MODEL

@st.cache_resource
def get_model():
    return genai.GenerativeModel(model_name="gemini-2.5-flash")

model = get_model()


# 6. USER INTERFACE

st.sidebar.info(
    "💡 **End-to-End Orchestration:** This page acts as the final workflow manager. "
    "Uploading an image here sequentially triggers the Extraction Agent, the Intent Agent, "
    "and synthesizes both outputs into a clean enterprise case ticket."
)

uploaded_file = st.file_uploader(
    "Upload Submission Document to Execute Full Pipeline (JPEG / PNG)", 
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    col_img, col_data = st.columns([1, 1.2])
    
    with col_img:
        st.image(uploaded_file, caption="Inbound Submission Payload", use_column_width=True)
        
    with col_data:
        if st.button("⚙️ Execute Full Multi-Agent Pipeline", type="primary", use_container_width=True):
            file_bytes = uploaded_file.getvalue()
            img_payload = {"mime_type": uploaded_file.type, "data": file_bytes}
            
            # --- NODE 1: SILENT EXTRACTION ---
            with st.spinner("🤖 Node 1: Extracting structured parameters..."):
                try:
                    res1 = model.generate_content(
                        contents=["Extract all parameters from this document layout.", img_payload],
                        generation_config=genai.GenerationConfig(
                            response_mime_type="application/json", response_schema=ExtractedDataSchema, temperature=0.0
                        )
                    )
                    node1_json = res1.text
                except Exception as e:
                    st.error(f"Node 1 Failed: {str(e)}")
                    st.stop()
                    
            # --- NODE 2: SILENT INTENT CLASSIFICATION ---
            with st.spinner("🏢 Node 2: Classifying business intent..."):
                try:
                    res2 = model.generate_content(
                        contents=["Analyze document layout to determine business intent.", img_payload],
                        generation_config=genai.GenerationConfig(
                            response_mime_type="application/json", response_schema=IntentSchema, temperature=0.0
                        )
                    )
                    node2_json = res2.text
                except Exception as e:
                    st.error(f"Node 2 Failed: {str(e)}")
                    st.stop()
                    
            # --- NODE 3: SYNTHESIS ---
            with st.spinner("📝 Node 3: Synthesizing parameters into CRM Case Record..."):
                try:
                    synthesis_prompt = f"""
                    Synthesize the following upstream agent payloads into a single, standardized corporate Case Record.
                    
                    NODE 1 EXTRACTED DATA:
                    {node1_json}
                    
                    NODE 2 INTENT DATA:
                    {node2_json}
                    """
                    
                    res3 = model.generate_content(
                        contents=[synthesis_prompt],
                        generation_config=genai.GenerationConfig(
                            response_mime_type="application/json", response_schema=CaseRecord, temperature=0.1
                        )
                    )
                    
                    case = CaseRecord.model_validate_json(res3.text)
                    
                    # --- DISPLAY COMPREHENSIVE OUTPUT DASHBOARD ---
                    st.success("🎉 End-to-End Orchestration Complete!")
                    st.divider()
                    
                    m_col1, m_col2, m_col3 = st.columns(3)
                    with m_col1:
                        st.metric("Priority SLA", case.priority)
                    with m_col2:
                        st.metric("Assigned Queue", case.assigned_queue)
                    with m_col3:
                        if case.flagged_issues != "None":
                            st.error("⚠️ Action Required")
                        else:
                            st.success("✨ Ready for Core Sync")
                            
                    st.markdown(f"### 📋 {case.case_title}")
                    
                    st.markdown("#### Executive Summary")
                    st.info(case.executive_summary)
                    
                    st.markdown("#### Flagged Issues / Operational Anomalies")
                    if case.flagged_issues == "None":
                        st.write("✅ All data parameters passed structural validation tests.")
                    else:
                        st.warning(case.flagged_issues)
                        
                    st.markdown("#### Synthesized Core System API Payload")
                    st.json(case.crm_payload)
                    
                except Exception as e:
                    st.error(f"Node 3 Synthesis Failed: {str(e)}")