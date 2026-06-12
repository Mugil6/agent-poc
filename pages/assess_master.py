import streamlit as st
import time
import json
from typing import Literal
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="Assess Master", layout="wide")
st.title("📊 Quote & Assess Workflow (Agentic Node)")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.1-flash-lite")

# AGENTIC SCHEMAS
class EnrichmentSchema(BaseModel):
    agent_scratchpad: str = Field(description="Reasoning: Why does this entity fall into this specific risk tier?")
    industry_risk_tier: Literal["LOW", "MODERATE", "HIGH", "SEVERE"]
    historical_claims_prob: int
    geographical_hazards: str

class RatingSchema(BaseModel):
    agent_scratchpad: str = Field(description="Actuarial Math Trace: Show the step-by-step multiplier calculation.")
    base_premium: str
    risk_multiplier: float
    final_premium: str

class SummarySchema(BaseModel):
    approval_status: Literal["APPROVED", "REFER", "DECLINED"]
    uw_executive_summary: str

class QuoteSchema(BaseModel):
    quote_id: str
    premium_display: str
    subjectivities: str

# MASTER ORCHESTRATION LOGIC

n3_data = st.session_state.get("n3_data")

if not n3_data:
    st.warning("⚠️ Run Intake Workflow first.")
else:
    if st.button("🚀 Execute Agentic Assess Workflow", type="primary", use_container_width=True):
        with st.status("Agent performing actuarial assessment...", expanded=True) as status:
            try:
                res5 = model.generate_content(
                    [f"Fetch external risk data. Show reasoning in scratchpad: {n3_data}"],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=EnrichmentSchema)
                )
                st.session_state.n5_data = res5.text
                time.sleep(4) 

                res6 = model.generate_content(
                    [f"Calculate commercial premium based on hazard profile. Show math trace in scratchpad: {res5.text}"],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=RatingSchema)
                )
                st.session_state.n6_data = res6.text
                time.sleep(4) 

                res7 = model.generate_content(
                    [f"Summarize risk status. Risk: {res5.text}, Price: {res6.text}"],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=SummarySchema)
                )
                st.session_state.n7_data = res7.text
                time.sleep(4) 

                res8 = model.generate_content(
                    [f"Draft quote based on: {res6.text}"],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=QuoteSchema)
                )
                st.session_state.n8_data = res8.text
                
                status.update(label="Agentic Assess Complete!", state="complete", expanded=False)

            except Exception as e:
                status.update(label=f"Workflow Failed: {str(e)}", state="error")
                st.stop()

    if st.session_state.get("n5_data") and st.session_state.get("n8_data"):
        st.success("🎉 Agent successfully rated the risk.")
        
        n5 = json.loads(st.session_state.n5_data)
        n6 = json.loads(st.session_state.n6_data)
        n7 = json.loads(st.session_state.n7_data)
        n8 = json.loads(st.session_state.n8_data)
        
        st.markdown("### 🧠 Agentic Reasoning Trace (Audit Log)")
        st.info(f"**Hazard Evaluation:** {n5.get('agent_scratchpad', 'N/A')}")
        st.info(f"**Actuarial Math Trace:** {n6.get('agent_scratchpad', 'N/A')}")
        st.divider()

        c1, c2, c3 = st.columns(3)
        c1.metric("System Decision", n7["approval_status"])
        c2.metric("Final Premium", n6["final_premium"])
        c3.metric("Industry Risk Tier", n5["industry_risk_tier"])
        
        with st.expander(f"📄 View Formal Quote: {n8['quote_id']}", expanded=True):
            st.markdown(f"**Total Valid Premium:** {n8['premium_display']}")
            st.error(f"**Subjectivities:** {n8['subjectivities']}")