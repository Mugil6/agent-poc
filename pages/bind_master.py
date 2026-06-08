import streamlit as st
import time
import json
from typing import List
from pydantic import BaseModel, Field
import google.generativeai as genai

st.set_page_config(page_title="Bind Master", layout="wide")
st.title("🤝 Negotiate & Bind Workflow (Master Agent)")
st.markdown("### Orchestrating Nodes 9-10 (Raw Text Fallback)")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-3.1-flash-lite")

# SCHEMAS
class CrossSellItem(BaseModel):
    product_name: str = Field(description="Name of the suggested insurance product or endorsement.")
    rationale: str = Field(description="Deep actuarial explanation of why this product fits.")
    estimated_additional_premium: str = Field(description="Realistic estimated cost addition in USD.")

class CrossSellList(BaseModel):
    opportunities: List[CrossSellItem] = Field(description="List of highly relevant cross-sell opportunities.")

# MASTER ORCHESTRATION LOGIC
n5_data = st.session_state.get("n5_data")
n8_data = st.session_state.get("n8_data")

if not n5_data or not n8_data:
    st.warning("⚠️ Missing dependencies. Please run the Assess Workflow first.")
else:
    if st.button("🚀 Execute Dynamic Bind Workflow", type="primary", use_container_width=True):
        with st.status("Master Agent executing comprehensive Bind tasks...", expanded=True) as status:
            try:
                # SUB-AGENT 9 (JSON Mode for Data)
                status.update(label="Master Agent: Analyzing risk profile for cross-sells...")
                res9 = model.generate_content(
                    [f"Analyze the Risk Profile: {n5_data} and the Quote: {n8_data}. Suggest ALL logical, highly relevant cross-sell and upsell products. Provide comprehensive rationale for each."],
                    generation_config=genai.GenerationConfig(response_mime_type="application/json", response_schema=CrossSellList)
                )
                st.session_state.n9_data = res9.text
                status.update(label="✅ Comprehensive upsell portfolio generated.")
                
                time.sleep(2)

                # SUB-AGENT 10 (Raw Text Mode for Email)
                status.update(label="Master Agent: Drafting extensive Broker Dispatch Communication...")
                
                email_prompt = f"""
                Draft a persuasive, enterprise-grade, extensive dispatch email to a broker providing this Quote: {n8_data}. 
                Strategically pitch these specific Upsells: {res9.text}.
                
                FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
                SUBJECT: [Your engaging subject line here]
                BODY:
                [Your full email body here]
                """
                
                res10 = model.generate_content([email_prompt])
                st.session_state.n10_raw_text = res10.text
                
                status.update(label="Bind Workflow Complete!", state="complete", expanded=False)

            except Exception as e:
                status.update(label=f"Workflow Failed: {str(e)}", state="error")
                st.stop()

    #  FINAL DASHBOARD
    if st.session_state.get("n9_data") and st.session_state.get("n10_raw_text"):
        st.success("🎉 Master Agent successfully executed.")
        st.divider()
        
        try:
            # 1. Parse Node 9 JSON
            n9 = json.loads(st.session_state.n9_data)
            
            st.markdown("#### 📈 Predictive Cross-Sell Portfolio (Node 9)")
            opportunities = n9.get("opportunities", [])
            
            if not opportunities:
                st.info("No logical cross-sells identified for this specific risk profile.")
            else:
                for idx, item in enumerate(opportunities):
                    with st.expander(f"Opportunity {idx+1}: {item.get('product_name', 'Unknown')} ({item.get('estimated_additional_premium', 'TBD')})", expanded=True):
                        st.write(item.get("rationale", ""))

            # 2. Parse Node 10 Raw Text manually (Safeguard against JSON limitations)
            raw_email = st.session_state.n10_raw_text
            subject_line = "Your Formal Insurance Quote & Coverage Enhancements"
            email_body = raw_email
            
            if "BODY:" in raw_email:
                parts = raw_email.split("BODY:")
                subject_line = parts[0].replace("SUBJECT:", "").strip()
                email_body = parts[1].strip()

            st.markdown("#### ✉️ Final Broker Dispatch (Node 10)")
            st.text_input("Subject", value=subject_line)
            st.text_area("Email Body", value=email_body, height=400)
            
        except Exception as e:
            st.error(f"Failed to render dashboard. Error: {str(e)}")