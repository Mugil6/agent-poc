import streamlit as st
import time
import json
from typing import Literal
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="Assess Master", layout="wide")
st.title("📊 Quote & Assess Workflow (Master Agent)")
st.markdown("### Orchestrating Nodes 5-8 Automatically")


genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.1-flash-lite")

#  SCHEMAS
class EnrichmentSchema(BaseModel):
    industry_risk_tier: Literal["LOW", "MODERATE", "HIGH", "SEVERE"] = Field(description="Strict categorization of industry risk.")
    historical_claims_prob: int = Field(description="Probability out of 100.")
    geographical_hazards: str = Field(description="Detailed list of environmental risks (e.g., Flood Zone, Wildfire).")
    compliance_flags: str = Field(description="Regulatory flags specific to this state and industry.")

class RatingSchema(BaseModel):
    base_premium: str = Field(description="Calculated base premium formatted as USD.")
    risk_multiplier: float = Field(description="Decimal multiplier applied based on hazard data.")
    final_premium: str = Field(description="Final premium formatted as USD.")
    pricing_rationale: str = Field(description="A detailed, 2-sentence actuarial explanation of the multiplier.")

class SummarySchema(BaseModel):
    approval_status: Literal["APPROVED_FOR_QUOTE", "REFER_TO_SENIOR_UW", "DECLINED"]
    uw_executive_summary: str = Field(description="A comprehensive executive summary for the human underwriter.")
    key_nuances: str = Field(description="Critical bullet points combining the case intent and the hazard profile.")

class QuoteSchema(BaseModel):
    quote_id: str = Field(description="Standardized ID, e.g., QTE-2026-XYZ")
    coverage_pitch: str = Field(description="Professional paragraph outlining limits and inclusions.")
    premium_display: str = Field(description="Cleanly formatted premium string.")
    subjectivities: str = Field(description="Conditions precedent to binding (e.g., 'Subject to loss runs').")

# MASTER ORCHESTRATION LOGIC
n3_data = st.session_state.get("n3_data")

if not n3_data:
    st.warning(" No Case Record found. Please run the Intake Workflow first.")
else:
    # Display the inbound payload from Phase 1 cleanly
    with st.expander("📥 View Inbound Case Record (From Intake Node 3)", expanded=False):
        try:
            st.json(json.loads(n3_data))
        except:
            st.text(n3_data)

    if st.button("🚀 Execute Autonomous Assess Workflow", type="primary", use_container_width=True):
        
        with st.status("Master Agent initializing Assess phase...", expanded=True) as status:
            try:
                # --- SUB-AGENT 5: ENRICHMENT ---
                status.update(label="Master Agent: Delegating to External Enrichment Node...")
                res5 = model.generate_content(
                    [f"Simulate fetching detailed external geo and compliance risk data for this entity: {n3_data}"],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=EnrichmentSchema)
                )
                st.session_state.n5_data = res5.text
                st.write("✅ External risk data fetched.")
                time.sleep(5) # Paced for safety

                # --- SUB-AGENT 6: RATING ---
                status.update(label="Master Agent: Delegating to Actuarial Rating Engine...")
                res6 = model.generate_content(
                    [f"Calculate commercial premium based on this specific hazard profile. Be detailed in the rationale: {res5.text}"],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=RatingSchema)
                )
                st.session_state.n6_data = res6.text
                st.write("✅ Premium calculated.")
                time.sleep(5) 

                # SUB-AGENT 7: SUMMARIZATION
                status.update(label="Master Agent: Synthesizing Underwriter Decision Support...")
                res7 = model.generate_content(
                    [f"Act as a Senior UW. Summarize risk and recommend status. Case: {n3_data}, Risk: {res5.text}, Price: {res6.text}"],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=SummarySchema)
                )
                st.session_state.n7_data = res7.text
                st.write("✅ Executive summary generated.")
                time.sleep(5) 

                # SUB-AGENT 8: QUOTE PREP
                status.update(label="Master Agent: Drafting Formal Quote Document...")
                res8 = model.generate_content(
                    [f"Draft a formal, highly professional insurance quote based on this rating data: {res6.text}"],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=QuoteSchema)
                )
                st.session_state.n8_data = res8.text
                st.write("✅ Quote document drafted.")
                
                status.update(label="Assess Workflow Complete!", state="complete", expanded=False)

            except Exception as e:
                status.update(label=f"Workflow Failed: {str(e)}", state="error")
                st.stop()

        #  DASHBOARD
        st.success("🎉 Master Agent successfully orchestrated all Assess nodes.")
        st.divider()
        
        n5 = json.loads(st.session_state.n5_data)
        n6 = json.loads(st.session_state.n6_data)
        n7 = json.loads(st.session_state.n7_data)
        n8 = json.loads(st.session_state.n8_data)
        
        # TOP METRICS
        c1, c2, c3 = st.columns(3)
        c1.metric("System Decision", n7["approval_status"].replace("_", " "))
        c2.metric("Final Premium", n6["final_premium"])
        c3.metric("Industry Risk Tier", n5["industry_risk_tier"])
        
        # UI EXPANDERS FOR DEEP DIVE
        with st.expander("⚖️ View UW Decision Support & Pricing (Nodes 6 & 7)", expanded=True):
            st.info(n7["uw_executive_summary"])
            st.warning(f"**Key Nuances & Hazards:** {n7['key_nuances']} | {n5['geographical_hazards']}")
            st.markdown("---")
            st.markdown("##### Actuarial Breakdown")
            col_a, col_b = st.columns(2)
            col_a.write(f"**Base Premium:** {n6['base_premium']}")
            col_b.write(f"**Risk Multiplier:** x{n6['risk_multiplier']}")
            st.caption(f"*Rationale:* {n6['pricing_rationale']}")
            
        with st.expander(f"📄 View Formal Quote Draft: {n8['quote_id']} (Node 8)", expanded=False):
            st.write(n8["coverage_pitch"])
            st.markdown(f"**Total Valid Premium:** {n8['premium_display']}")
            st.error(f"**Subjectivities:** {n8['subjectivities']}")