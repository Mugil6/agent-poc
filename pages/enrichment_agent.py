import streamlit as st
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="Enrichment Agent", layout="wide")
st.title("🌐 External Data Enrichment")
st.markdown("### Workflow 2: Quote & Assess (Node 5)")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

class EnrichmentData(BaseModel):
    industry_risk_tier: str = Field(description="Classify industry risk as LOW, MODERATE, HIGH, or SEVERE.")
    historical_claims_prob: int = Field(description="Probability (0-100) of past claims.")
    geographical_hazards: str = Field(description="Potential geo-risks based on location.")
    compliance_flags: str = Field(description="Regulatory flags associated with entity.")

model = genai.GenerativeModel("gemini-2.5-flash")

case_data = st.session_state.get("node3_case_record")
st.text_area("Inbound Case Record", value=case_data if case_data else "Awaiting Node 3 execution...", height=150)

if st.button("🌐 Fetch External Risk Data", type="primary", disabled=not case_data):
    with st.spinner("Querying external data..."):
        res = model.generate_content(
            contents=[f"Simulate fetching external geo and compliance risk data for this entity: {case_data}"],
            generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=EnrichmentData)
        )
        data = EnrichmentData.model_validate_json(res.text)
        st.session_state.node5_enrichment_data = res.text
        
        c1, c2 = st.columns(2)
        c1.metric("Risk Tier", data.industry_risk_tier)
        c2.metric("Claim Probability", f"{data.historical_claims_prob}%")
        st.warning(f"Hazards: {data.geographical_hazards}")
        st.info(f"Compliance: {data.compliance_flags}")