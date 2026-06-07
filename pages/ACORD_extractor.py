import streamlit as st
import pandas as pd
from typing import List
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="ACORD Extractor", layout="wide")
st.title("🔍 Structured Data Extractor")
st.markdown("### Workflow 1: Intake & Triage (Node 1)")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

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

class ACORDData(BaseModel):
    producer_name: str = Field(description="Full name of the producer")
    insured_name: str = Field(description="Name of the insured entity")
    insured_address: Address = Field(description="Split address components")
    companies_affording_coverage: List[CompanyCoverage]
    policies: List[PolicyData]
    limits: List[CoverageLimit]

model = genai.GenerativeModel("gemini-2.5-flash")

if "global_file_bytes" in st.session_state and st.session_state.global_file_bytes:
    col_img, col_data = st.columns([1, 1.2])
    with col_img:
        st.image(st.session_state.global_file_bytes, caption="Active Payload", use_column_width=True)
    with col_data:
        if st.button("🔍 Execute Extraction Agent", type="primary", use_container_width=True):
            with st.spinner("Parsing grid into structured tables..."):
                try:
                    img_payload = {"mime_type": st.session_state.global_mime_type, "data": st.session_state.global_file_bytes}
                    res = model.generate_content(
                        contents=["Extract all parameters from this document layout.", img_payload],
                        generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=ACORDData, temperature=0.0)
                    )
                    data = ACORDData.model_validate_json(res.text)
                    st.session_state.node1_extracted_data = res.text
                    
                    st.success(" Extraction Complete")
                    
                    # UI Render: Entity Data
                    st.markdown("#### Entity Information")
                    st.write(f"**Producer:** {data.producer_name}")
                    st.write(f"**Insured:** {data.insured_name}")
                    st.write(f"**Address:** {data.insured_address.street}, {data.insured_address.city}, {data.insured_address.state} {data.insured_address.zip_code}")
                    
                    # UI Render: DataFrames
                    st.markdown("#### Carrier Details")
                    st.dataframe(pd.DataFrame([c.model_dump() for c in data.companies_affording_coverage]), use_container_width=True)
                    
                    st.markdown("#### Active Policies")
                    st.dataframe(pd.DataFrame([p.model_dump() for p in data.policies]), use_container_width=True)
                    
                    st.markdown("#### Liability Limits")
                    st.dataframe(pd.DataFrame([l.model_dump() for l in data.limits]), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Extraction failed: {str(e)}")
else:
    st.warning(" No document found in global memory.")