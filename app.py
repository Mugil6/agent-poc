import streamlit as st

st.set_page_config(page_title="P&C Underwriting OS", page_icon="🛡️", layout="wide")
st.title("🛡️ Enterprise P&C Underwriting OS")

# Global Session State Initialization
memory_keys = [
    "global_file_bytes", "global_mime_type", "node1_extracted_data", "node2_intent_data", 
    "node3_case_record", "node4_exception_email", "node5_enrichment_data", "node6_rating_data", 
    "node7_summary_data", "node8_quote_data", "node9_cross_sell_data", "node10_issuance_data"
]
for key in memory_keys:
    if key not in st.session_state:
        st.session_state[key] = None

st.markdown("### 📥 Global Document Upload")
uploaded_file = st.file_uploader("Upload Broker Payload (JPEG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.session_state.global_file_bytes = uploaded_file.getvalue()
    st.session_state.global_mime_type = uploaded_file.type
    st.success(" Payload cached. Proceed to Workflow 1.")
elif st.session_state.global_file_bytes:
    st.success(" Payload active in global memory.")
    if st.button("Clear Memory"):
        for key in memory_keys:
            st.session_state[key] = None
        st.rerun()

st.divider()

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### 📥 Workflow 1: Intake")
    st.markdown("1. **Extractor:** Maps tabular data.\n2. **Classifier:** Determines intent.\n3. **Case Creator:** Synthesizes CRM record.\n4. **Exception Agent:** Drafts emails for missing data.")
with c2:
    st.markdown("### 📊 Workflow 2: Quote & Assess")
    st.markdown("5. **Enrichment:** External risk data.\n6. **Rating:** Calculates premium.\n7. **Summarization:** UW decision support.\n8. **Quote Prep:** Drafts formal document.")
with c3:
    st.markdown("### 🤝 Workflow 3: Negotiate & Bind")
    st.markdown("9. **Cross-Sell:** Identifies upsell models.\n10. **Issuance:** Drafts final broker communication.")