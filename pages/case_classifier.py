import streamlit as st
import os
from typing import Literal
from pydantic import BaseModel, Field
import google.generativeai as genai

# =====================================================================
# 1. UI CONFIGURATION
# =====================================================================
st.set_page_config(page_title="Case Classifier", layout="wide")
st.title("🏢 P&C Case Classification Agent")
st.markdown("### Multi-Agent Pipeline: Node 2 (Business Logic)")

# =====================================================================
# 2. SECURE API KEY HANDLING
# =====================================================================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    os.environ["GEMINI_API_KEY"] = api_key
    genai.configure(api_key=api_key)
except KeyError:
    st.error("⚠️ **Setup Error:** GEMINI_API_KEY not found in secrets.")
    st.stop()

# =====================================================================
# 3. SCHEMA DEFINITION (Bookroll vs. New Business)
# =====================================================================
CaseType = Literal[
    "BOOKROLL", 
    "NEW_BUSINESS", 
    "ESCALATE_TO_HUMAN"
]

class CaseClassification(BaseModel):
    case_type: CaseType = Field(description="Classify as BOOKROLL (bulk transfer of policies) or NEW_BUSINESS (single/few new policies).")
    confidence_score: int = Field(description="Confidence score of the classification from 1 to 100.")
    detected_policy_count: str = Field(description="Estimated number of policies or accounts visible in the document. Output 'UNKNOWN' if unclear.")
    key_indicators: str = Field(description="List the visual key phrases or data points that led to this decision (e.g., 'table with 50 rows', 'single applicant name').")
    reasoning: str = Field(description="A brief 1-2 sentence explanation of the classification based on the image.")

# =====================================================================
# 4. INITIALIZE THE CASE CLASSIFICATION MODEL
# =====================================================================
@st.cache_resource
def get_case_agent():
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=(
            "You are an elite P&C Insurance Underwriting Agent. Your job is to visually analyze the uploaded document image "
            "and classify the business intent. "
            "A 'Bookroll' involves an agency moving a large portfolio/book of existing policies. Visually, this usually looks like "
            "a spreadsheet, a schedule of vehicles/properties with dozens of rows, or bulk loss runs. "
            "'New Business' is typically a single application (like an ACORD 125/130) for one specific insured entity. "
            "If the document is too blurry or ambiguous to tell, choose 'ESCALATE_TO_HUMAN'."
        )
    )

model = get_case_agent()

# =====================================================================
# 5. USER INTERFACE
# =====================================================================
st.sidebar.info(
    "💡 **Pipeline Context:** This agent determines the business workflow based on document structure. "
    "Spreadsheets and bulk schedules route to the Bookroll pipeline; single ACORD forms go to standard New Business underwriting."
)

uploaded_file = st.file_uploader(
    "Upload Submission Document (JPEG / PNG)", 
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    col_img, col_data = st.columns([1, 1.2])
    
    with col_img:
        st.image(uploaded_file, caption="Inbound Document", use_column_width=True)
        
    with col_data:
        if st.button("🧠 Analyze Visual Case Intent", type="primary", use_container_width=True):
            with st.spinner("Analyzing document layout and business context..."):
                try:
                    # Get raw file bytes
                    file_bytes = uploaded_file.getvalue()
                    
                    response = model.generate_content(
                        contents=[
                            "Visually analyze this document and classify the case intent.",
                            {"mime_type": uploaded_file.type, "data": file_bytes}
                        ],
                        generation_config=genai.GenerationConfig(
                            response_mime_type="application/json",
                            response_schema=CaseClassification,
                            temperature=0.1
                        )
                    )
                    
                    # Validate JSON to Pydantic
                    data = CaseClassification.model_validate_json(response.text)
                    
                    # Display Results Dashboard
                    if data.case_type == "ESCALATE_TO_HUMAN":
                        st.error("⚠️ Case Flagged: Ambiguous Document - Escalate to Human")
                    elif data.case_type == "BOOKROLL":
                        st.success("📚 Case Classified: BOOKROLL (Bulk Processing Queue)")
                    else:
                        st.info("📄 Case Classified: NEW BUSINESS (Standard Queue)")
                        
                    st.divider()
                    
                    # Layout metrics
                    m_col1, m_col2, m_col3 = st.columns(3)
                    with m_col1:
                        st.metric("Primary Intent", data.case_type.replace('_', ' '))
                    with m_col2:
                        st.metric("Confidence Score", f"{data.confidence_score}%")
                    with m_col3:
                        st.metric("Visible Policies", data.detected_policy_count)
                    
                    st.divider()
                    st.markdown("#### Agent Visual Reasoning")
                    st.write(data.reasoning)
                    
                    st.markdown("#### Key Layout Indicators Detected")
                    st.write(data.key_indicators)
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")