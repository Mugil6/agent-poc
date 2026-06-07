import streamlit as st
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="Issuance Agent", layout="wide")
st.title("✉️ Broker Issuance Agent")
st.markdown("### Workflow 3: Negotiate & Bind (Node 10)")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

class FinalDispatch(BaseModel):
    email_subject: str = Field(description="Subject line for quote dispatch.")
    email_body: str = Field(description="Email presenting the quote, highlighting the cross-sell options, and outlining binding instructions.")

model = genai.GenerativeModel("gemini-2.5-flash")

quote = st.session_state.get("node8_quote_data", "{}")
upsell = st.session_state.get("node9_cross_sell_data", "{}")

if st.button("✉️ Draft Final Broker Dispatch", type="primary"):
    with st.spinner("Drafting broker communication..."):
        res = model.generate_content(
            contents=[f"Draft a dispatch email providing this Quote: {quote} and pitching these Upsells: {upsell}"],
            generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=FinalDispatch)
        )
        data = FinalDispatch.model_validate_json(res.text)
        st.session_state.node10_issuance_data = res.text
        
        st.success("✅ Workflow Complete. Ready for dispatch.")
        st.text_input("Subject", value=data.email_subject)
        st.text_area("Body", value=data.email_body, height=300)