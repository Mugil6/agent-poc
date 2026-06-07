import streamlit as st
from typing import List
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="Cross Sell Agent", layout="wide")
st.title("📈 Cross-Sell / Up-Sell Agent")
st.markdown("### Workflow 3: Negotiate & Bind (Node 9)")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

class CrossSellItem(BaseModel):
    product_name: str = Field(description="Suggested product (e.g., Cyber, Umbrella).")
    rationale: str = Field(description="Why it fits this specific entity's profile.")

class CrossSellRecommendations(BaseModel):
    opportunities: List[CrossSellItem]

model = genai.GenerativeModel("gemini-2.5-flash")

quote = st.session_state.get("node8_quote_data")
enrich = st.session_state.get("node5_enrichment_data")

if st.button("📈 Analyze Upsell Opportunities", type="primary", disabled=not quote):
    with st.spinner("Running predictive models..."):
        res = model.generate_content(
            contents=[f"Suggest 2 cross-sell products based on Quote: {quote} and Risk: {enrich}"],
            generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=CrossSellRecommendations)
        )
        st.session_state.node9_cross_sell_data = res.text
        data = CrossSellRecommendations.model_validate_json(res.text)
        
        for item in data.opportunities:
            with st.expander(f"Opportunity: {item.product_name}"):
                st.write(item.rationale)