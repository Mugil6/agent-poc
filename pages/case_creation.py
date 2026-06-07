import streamlit as st
import json
from typing import Literal
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="Case Creator", layout="wide")
st.title("📝 Automated Case Creation Agent")
st.markdown("### Workflow 1: Intake & Triage (Node 3)")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

PriorityLevel = Literal["LOW", "MEDIUM", "HIGH", "URGENT"]

class CaseRecord(BaseModel):
    client_name: str = Field(description="Extracted name of the primary insured entity.")
    case_title: str = Field(description="Standardized title (e.g., 'New Business Submission - Acme Corp').")
    priority: PriorityLevel = Field(description="Determine SLA priority.")
    assigned_queue: str = Field(description="The operational team this should route to.")
    executive_summary: str = Field(description="A 2-3 sentence summary.")
    flagged_issues: str = Field(description="List missing fields. Output 'None' if perfectly clean.")
    crm_payload: str = Field(description="A stringified JSON object of core fields (e.g., Name, Status, Source, Expected Value).")

model = genai.GenerativeModel("gemini-2.5-flash")

n1 = st.session_state.get("node1_extracted_data", "")
n2 = st.session_state.get("node2_intent_data", "")

if not n1 or not n2:
    st.warning(" Please run Node 1 and Node 2 first.")
else:
    if st.button("⚙️ Synthesize System Record", type="primary"):
        with st.spinner("Synthesizing multi-agent data into CRM record..."):
            try:
                res = model.generate_content(
                    contents=[f"Synthesize into Case Record. Flag 'MISSING' data as high priority.\nNode 1: {n1}\nNode 2: {n2}"],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=CaseRecord, temperature=0.1)
                )
                case = CaseRecord.model_validate_json(res.text)
                st.session_state.node3_case_record = res.text
                
                st.success(" Case Record Synthesized")
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Priority SLA", case.priority)
                c2.metric("Assigned Queue", case.assigned_queue)
                if case.flagged_issues != "None":
                    c3.error(" Action Required")
                else:
                    c3.success(" Clean Record")

                st.markdown(f"### 📋 {case.case_title}")
                st.info(case.executive_summary)
                
                if case.flagged_issues != "None":
                    st.markdown("#### 🚩 Flagged Issues")
                    st.warning(case.flagged_issues)
                    
                # Clean UI for the CRM Payload (No Raw JSON)
                st.markdown("#### 💻 Core System Injection Ready")
                try:
                    payload_dict = json.loads(case.crm_payload)
                    for key, value in payload_dict.items():
                        st.write(f"**{str(key).replace('_', ' ').title()}:** {value}")
                except:
                    st.write(case.crm_payload) # Fallback if model fails strict JSON stringification
                    
            except Exception as e:
                st.error(f"Synthesis failed: {str(e)}")