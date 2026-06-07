import streamlit as st
from typing import Literal
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="Intent Classifier", layout="wide")
st.title("🏢 Business Intent Classifier")
st.markdown("### Workflow 1: Intake & Triage (Node 2)")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

CaseType = Literal["BOOKROLL", "NEW_BUSINESS", "ESCALATE_TO_HUMAN"]

class CaseClassification(BaseModel):
    case_type: CaseType = Field(description="Classify as BOOKROLL or NEW_BUSINESS.")
    confidence_score: int = Field(description="Confidence score (1-100).")
    detected_policy_count: str = Field(description="Estimated number of policies.")
    key_indicators: str = Field(description="Specific visual data points that led to this decision.")
    detailed_reasoning: str = Field(description="A thorough, step-by-step explanation of the visual and structural clues used to determine the intent.")

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="You are an expert document analyst. Do not give generic reasons. Explicitly state the visual structures (e.g., 'A 5-column grid with multiple vehicles indicates a schedule/bookroll' or 'A single ACORD 130 header indicates new business') that drove your classification."
)

if "global_file_bytes" in st.session_state and st.session_state.global_file_bytes:
    col_img, col_data = st.columns([1, 1.2])
    with col_img:
        st.image(st.session_state.global_file_bytes, caption="Active Payload", use_column_width=True)
    with col_data:
        if st.button("🏢 Execute Intent Classification", type="primary", use_container_width=True):
            with st.spinner("Performing deep structural analysis..."):
                try:
                    img_payload = {"mime_type": st.session_state.global_mime_type, "data": st.session_state.global_file_bytes}
                    res = model.generate_content(
                        contents=["Analyze document layout and explicitly explain the business intent.", img_payload],
                        generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=CaseClassification, temperature=0.1)
                    )
                    data = CaseClassification.model_validate_json(res.text)
                    st.session_state.node2_intent_data = res.text
                    
                    st.success(" Classification Complete")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Intent", data.case_type.replace('_', ' '))
                    c2.metric("Confidence", f"{data.confidence_score}%")
                    c3.metric("Visible Policies", data.detected_policy_count)
                    
                    st.markdown("#### Deep Agent Reasoning")
                    st.info(data.detailed_reasoning)
                    
                    st.markdown("#### Visual Clues Detected")
                    st.warning(data.key_indicators)
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
else:
    st.warning(" No document found in global memory.")