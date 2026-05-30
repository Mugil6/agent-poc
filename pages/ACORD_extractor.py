import streamlit as st
import os
from typing import List, Optional
from pydantic import BaseModel, Field
import google.generativeai as genai

# 1. UI CONFIGURATION
st.set_page_config(page_title="AI Underwriting Extractor", layout="wide")
st.title("📄 ACORD Underwriting Extractor")
st.markdown("### Native Gemini Ingestion PoC")

# 2. SECURE API KEY HANDLING
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    os.environ["GEMINI_API_KEY"] = api_key
    genai.configure(api_key=api_key)
except KeyError:
    st.error("⚠️ **Setup Error:** GEMINI_API_KEY not found in secrets. Please configure it.")
    st.stop()


# 3. SCHEMA DEFINITION

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

class ACORDData(BaseModel):
    producer_name: str = Field(description="Full name of the producer/agency")
    insured_name: str = Field(description="Name of the insured entity")
    insured_address: Address = Field(description="Split address components")
    insured_contact: str = Field(description="Contact details. Output 'MISSING' if not present.")
    companies_affording_coverage: List[CompanyCoverage] = Field(description="List of companies affording coverage")
    policies: List[PolicyData] = Field(description="List of policies")
    limits: List[CoverageLimit] = Field(description="List of coverage limits")

# 4. INITIALIZE THE NATIVE GEMINI MODEL

@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=(
            "You are an expert underwriting AI. Extract details from the provided ACORD form image. "
            "Map policy numbers, dates, and limits accurately. Output 'MISSING' if a field is unreadable."
        )
    )

model = get_model()


# 5. USER INTERFACE (FILE UPLOAD & EXTRACTION)

st.sidebar.info("💡 **Architecture Note:** This local PoC connects directly to Gemini via Google's API to avoid AWS credential locks. For production, this logic will be wrapped in AWS AgentCore for complete VPC isolation.")

uploaded_file = st.file_uploader(
    "Upload Underwriting Document (JPEG / PNG)", 
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    col_img, col_data = st.columns([1, 1.2])
    
    with col_img:
        st.image(uploaded_file, caption="Uploaded Document", use_column_width=True)
        
    with col_data:
        if st.button("🚀 Run Agentic Extraction", type="primary", use_container_width=True):
            with st.spinner("Analyzing document structure..."):
                try:
                    # Get raw file bytes
                    file_bytes = uploaded_file.getvalue()
                    
                    # Call Gemini directly and enforce the Pydantic schema
                    response = model.generate_content(
                        contents=[
                            "Extract all requested parameters from this document.",
                            {"mime_type": uploaded_file.type, "data": file_bytes}
                        ],
                        generation_config=genai.GenerationConfig(
                            response_mime_type="application/json",
                            response_schema=ACORDData,
                            temperature=0.1 # Low temperature for factual extraction
                        )
                    )
                    
                    # Validate the JSON string back into our Pydantic object
                    data = ACORDData.model_validate_json(response.text)
                    
                    # Display Results (Unchanged)
                    st.success("Extraction Complete!")
                    st.divider()
                    
                    m_col1, m_col2 = st.columns(2)
                    with m_col1:
                        st.metric("Producer", data.producer_name)
                        st.metric("Insured Account", data.insured_name)
                    with m_col2:
                        st.metric("Contact", data.insured_contact)
                        st.code(f"Street: {data.insured_address.street}\nCity:   {data.insured_address.city}\nState:  {data.insured_address.state}\nZip:    {data.insured_address.zip_code}")
                    
                    st.divider()
                    st.markdown("#### Carrier Matrix")
                    st.table([{"Letter": c.company_letter, "Name": c.company_name, "NAIC": c.naic_code} for c in data.companies_affording_coverage])
                        
                    st.divider()
                    st.markdown("#### Policies")
                    for policy in data.policies:
                        with st.expander(f"{policy.insurance_type} — {policy.policy_number}"):
                            st.write(f"**Effective:** {policy.effective_date} | **Expiration:** {policy.expiration_date} | **Tenure:** {policy.tenure}")
                            
                    st.divider()
                    st.markdown("#### Liability Limits")
                    st.dataframe([{"Type": l.limit_type, "Amount": l.limit_amount} for l in data.limits], hide_index=True)
                        
                except Exception as e:
                    st.error(f"Extraction failed: {str(e)}")