import streamlit as st
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="Quote Prep Agent", layout="wide")
st.title("📄 Quote Preparation Agent")
st.markdown("### Workflow 2: Quote & Assess (Node 8)")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

class QuoteDocument(BaseModel):
    quote_id: str = Field(description="Generated Quote ID (e.g., QTE-2026-XYZ)")
    coverage_pitch: str = Field(description="Professional paragraph outlining the coverages and limits.")
    premium_display: str = Field(description="Formatted premium and payment terms.")
    subjectivities: str = Field(description="Conditions required to bind (e.g., 'Subject to signed ACORD').")

model = genai.GenerativeModel("gemini-2.5-flash")

rating = st.session_state.get("node6_rating_data")

if st.button("📄 Generate Formal Quote", type="primary", disabled=not rating):
    with st.spinner("Drafting quote document..."):
        res = model.generate_content(
            contents=[f"Draft a formal insurance quote based on this rating data: {rating}"],
            generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=QuoteDocument)
        )
        data = QuoteDocument.model_validate_json(res.text)
        st.session_state.node8_quote_data = res.text
        
        st.success(f"✅ Quote {data.quote_id} Generated")
        st.write(data.coverage_pitch)
        st.metric("Total Premium", data.premium_display)
        st.warning(f"Subjectivities: {data.subjectivities}")