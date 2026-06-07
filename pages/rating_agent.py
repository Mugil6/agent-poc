import streamlit as st
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="Rating Agent", layout="wide")
st.title("🧮 Actuarial Rating Engine")
st.markdown("### Workflow 2: Quote & Assess (Node 6)")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

class RatingData(BaseModel):
    base_premium: str = Field(description="Base premium in USD.")
    risk_multiplier: float = Field(description="Multiplier applied based on hazard data.")
    final_premium: str = Field(description="Final calculated premium.")
    pricing_rationale: str = Field(description="Actuarial explanation of the multiplier.")

model = genai.GenerativeModel("gemini-2.5-flash")

enrichment_data = st.session_state.get("node5_enrichment_data")
st.text_area("Inbound Risk Profile", value=enrichment_data if enrichment_data else "Awaiting Node 5 execution...", height=150)

if st.button("🧮 Calculate Premium", type="primary", disabled=not enrichment_data):
    with st.spinner("Running rating models..."):
        res = model.generate_content(
            contents=[f"Calculate commercial premium based on this hazard profile: {enrichment_data}"],
            generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=RatingData)
        )
        data = RatingData.model_validate_json(res.text)
        st.session_state.node6_rating_data = res.text
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Base Premium", data.base_premium)
        c2.metric("Multiplier", f"x {data.risk_multiplier}")
        c3.metric("Final Premium", data.final_premium)
        st.info(data.pricing_rationale)