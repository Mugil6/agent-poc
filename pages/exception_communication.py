import streamlit as st
import os
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="Exception Agent", layout="wide")
st.title(" Exception Communicator")
st.markdown("### Workflow 1: Intake & Triage (Node 4)")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

class ExceptionEmail(BaseModel):
    action_required: bool = Field(description="True if issues are flagged in the Case Record, False if clean.")
    email_subject: str = Field(description="Subject line referencing the case title.")
    email_body: str = Field(description="Professional email to the broker requesting specific missing documents or fields.")

model = genai.GenerativeModel("gemini-2.5-flash")

case_data = st.session_state.get("node3_case_record")
st.text_area("Inbound Case Record (From Node 3)", value=case_data if case_data else "Awaiting Node 3 execution...", height=150)

if st.button("📧 Generate Exception Communication", type="primary", disabled=not case_data):
    with st.spinner("Analyzing case for missing information..."):
        res = model.generate_content(
            contents=[f"Read this case record. If 'flagged_issues' are present, draft an email to the broker requesting the missing info. If None, set action_required to false: {case_data}"],
            generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=ExceptionEmail)
        )
        data = ExceptionEmail.model_validate_json(res.text)
        st.session_state.node4_exception_email = res.text
        
        if data.action_required:
            st.warning(" Missing Information Detected. Communication Drafted.")
            st.text_input("Subject", value=data.email_subject)
            st.text_area("Body", value=data.email_body, height=200)
        else:
            st.success(" Case is perfectly clean. No exception communication required. Proceed to Quote & Assess.")