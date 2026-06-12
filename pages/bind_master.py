import streamlit as st
import time
import json
from typing import List
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="Bind Master", layout="wide")
st.title("🤝 Negotiate & Bind Workflow (Agentic Node)")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.1-flash-lite")

#  AGENTIC SCHEMAS
class CrossSellItem(BaseModel):
    product_name: str
    rationale: str
    estimated_additional_premium: str

class CrossSellList(BaseModel):
    agent_scratchpad: str = Field(description="Sales Strategy Trace: Analyze the hazard profile to determine the absolute best upsell strategy before listing the items.")
    opportunities: List[CrossSellItem]

# MASTER ORCHESTRATION LOGIC

n5_data = st.session_state.get("n5_data")
n8_data = st.session_state.get("n8_data")

if not n5_data or not n8_data:
    st.warning("⚠️ Run Assess Workflow first.")
else:
    if st.button("🚀 Execute Agentic Bind Workflow", type="primary", use_container_width=True):
        with st.status("Agent planning sales strategy...", expanded=True) as status:
            try:
                res9 = model.generate_content(
                    [f"Analyze Risk Profile: {n5_data} and Quote: {n8_data}. Formulate a sales strategy in the scratchpad, then list the cross-sells."],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=CrossSellList)
                )
                st.session_state.n9_data = res9.text
                time.sleep(2)

                res10 = model.generate_content([
                    f"Draft a long-form dispatch email providing Quote: {n8_data}. Pitch these Upsells strategically: {res9.text}. FORMAT: SUBJECT: [Subj] \n BODY: [Body]"
                ])
                st.session_state.n10_raw_text = res10.text
                
                status.update(label="Agentic Bind Complete!", state="complete", expanded=False)

            except Exception as e:
                status.update(label=f"Workflow Failed: {str(e)}", state="error")
                st.stop()

    if st.session_state.get("n9_data") and st.session_state.get("n10_raw_text"):
        st.success("🎉 Agent successfully drafted communications.")
        
        try:
            n9 = json.loads(st.session_state.n9_data)
            
            st.markdown("### 🧠 Agentic Reasoning Trace (Audit Log)")
            st.info(f"**Sales Strategy Planning:** {n9.get('agent_scratchpad', 'N/A')}")
            st.divider()

            st.markdown("#### 📈 Predictive Cross-Sell Portfolio")
            for idx, item in enumerate(n9.get("opportunities", [])):
                with st.expander(f"Opportunity {idx+1}: {item.get('product_name')} ({item.get('estimated_additional_premium')})"):
                    st.write(item.get("rationale"))

            raw_email = st.session_state.n10_raw_text
            subject_line = "Your Formal Insurance Quote"
            email_body = raw_email
            if "BODY:" in raw_email:
                parts = raw_email.split("BODY:")
                subject_line = parts[0].replace("SUBJECT:", "").strip()
                email_body = parts[1].strip()

            st.markdown("#### ✉️ Final Broker Dispatch")
            st.text_input("Subject", value=subject_line)
            st.text_area("Email Body", value=email_body, height=300)
            
            st.markdown("### 💬 Human-in-the-Loop Revision")
            feedback = st.text_area("Give the Agent feedback (e.g., 'Make it more urgent'):")
            if st.button("🔄 Refine Draft"):
                if feedback:
                    with st.spinner("Agent self-correcting..."):
                        revised = model.generate_content([f"Rewrite this email based on strictly on this feedback: '{feedback}'. Email: {raw_email}. FORMAT: SUBJECT: [Subj] \n BODY: [Body]"])
                        st.session_state.n10_raw_text = revised.text
                        st.rerun()

        except Exception as e:
            st.error(f"Failed to render dashboard. Error: {str(e)}")