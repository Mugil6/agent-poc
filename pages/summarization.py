import streamlit as st
from typing import Literal
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="Summarization Agent", layout="wide")
st.title("⚖️ UW Decision Support Agent")
st.markdown("### Workflow 2: Quote & Assess (Node 7)")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

class RiskSummary(BaseModel):
    approval_status: Literal["APPROVED_FOR_QUOTE", "REFER_TO_SENIOR_UW", "DECLINED"]
    uw_executive_summary: str = Field(description="A concise summary of the risk, pricing, and hazards for the human underwriter.")
    key_nuances: str = Field(description="Bullet points of critical nuances (e.g., high flood risk but clean claims history).")

model = genai.GenerativeModel("gemini-2.5-flash")

case = st.session_state.get("node3_case_record", "{}")
enrich = st.session_state.get("node5_enrichment_data", "{}")
rating = st.session_state.get("node6_rating_data", "{}")

if st.button("⚖️ Generate Decision Support", type="primary"):
    with st.spinner("Synthesizing pipeline data..."):
        res = model.generate_content(
            contents=[f"Act as a Senior UW. Summarize risk and recommend status based on:\nCase: {case}\nRisk: {enrich}\nPrice: {rating}"],
            generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=RiskSummary)
        )
        data = RiskSummary.model_validate_json(res.text)
        st.session_state.node7_summary_data = res.text
        
        st.metric("System Recommendation", data.approval_status.replace("_", " "))
        st.info(data.uw_executive_summary)
        st.warning(f"Key Nuances: {data.key_nuances}")