import streamlit as st

st.set_page_config(page_title="P&C Underwriting OS", page_icon="🛡️", layout="wide")
st.title("🛡️ Enterprise P&C Underwriting OS")

#  GLOBAL SESSION STATE INITIALIZATION
# We initialize the memory keys that the Master Agents will use
memory_keys = [
    "global_file_bytes", "global_mime_type", 
    "n1_data", "n2_data", "n3_data", "n4_data", 
    "n5_data", "n6_data", "n7_data", "n8_data", 
    "n9_data", "n10_data"
]

for key in memory_keys:
    if key not in st.session_state:
        st.session_state[key] = None

# GLOBAL UPLOAD WIDGET
st.markdown("### 📥 System Ingestion")
st.info("Upload an inbound broker submission. This payload will be cached globally and processed autonomously by the Master Agents.")

uploaded_file = st.file_uploader("Upload Broker Payload (JPEG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Save to global memory
    st.session_state.global_file_bytes = uploaded_file.getvalue()
    st.session_state.global_mime_type = uploaded_file.type
    st.success("✅ Payload securely cached in global memory. Proceed to the Intake Master.")
elif st.session_state.global_file_bytes:
    st.success("✅ A document is currently active in the system pipeline.")
    if st.button("Clear System Memory"):
        for key in memory_keys:
            st.session_state[key] = None
        st.rerun()

st.divider()

# ARCHITECTURE OVERVIEW (For Demo)
st.markdown("### 🧠 The Supervisor Architecture")
st.markdown(
    "This system utilizes a **Hierarchical Agent Pattern**. Instead of manual routing, "
    "three Master Supervisors orchestrate underlying specialized sub-agents."
)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("#### 1️⃣ Intake Master")
    st.markdown("Orchestrates structural mapping, intent classification, CRM ticket synthesis, and exception handling.")
    
with c2:
    st.markdown("#### 2️⃣ Assess Master")
    st.markdown("Orchestrates external data enrichment, actuarial premium rating, and quote generation.")
    
with c3:
    st.markdown("#### 3️⃣ Bind Master")
    st.markdown("Orchestrates predictive cross-sell modeling and final broker dispatch communications.")