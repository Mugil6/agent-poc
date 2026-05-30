# 🛡️ Agentic AI: Intelligent Intake & Orchestration Portal (PoC)

This repository contains a Proof of Concept (PoC) for an **Enterprise Multi-Agent Orchestration Pipeline**. It is designed to automate the classification and extraction of complex, highly-structured and unstructured business documents.

Built with **Streamlit's Multipage Architecture**, **Pydantic**, and the **Native Gemini API**, this application demonstrates how multimodal Large Language Models (LLMs) can act as deterministic reasoning nodes to parse spatial document layouts and classify business intent.

## 🏗️ Architecture: PoC vs. Production

This repository serves as **Phase 1 (Local/Cloud Demo)** to validate agentic reasoning and data extraction capabilities without requiring enterprise infrastructure overhead.

* **Phase 1 (Current PoC):** Utilizes `google.generativeai` (Gemini 2.5 Flash open weights) and Streamlit Community Cloud. This allows stakeholders to immediately interact with the UI, test sample documents, and validate extraction accuracy.
* **Phase 2 (Target Enterprise Architecture):** The extraction logic, prompt engineering, and Pydantic schemas built here are highly modular. Upon securing cloud provisioning, these Streamlit pages will be decoupled, wrapped in scalable agent SDKs (such as AWS AgentCore or similar frameworks), and deployed as isolated functions within a secure VPC for production processing.

## 🧠 The Agent Nodes

This portal is structured as a Microservices Architecture. Each "Page" represents a distinct, isolated AI Agent with a specific operational capability:

1. **🔍 Node 1: Structured Data Extractor**
   * **Function:** Navigates complex grid layouts and tabular formats inherent to standardized industry forms.
   * **Mechanism:** Enforces strict `Pydantic` schemas to force the LLM to output highly nested, deterministic JSON (mapping entity details, identification codes, and quantitative metrics) rather than conversational text.
2. **🏢 Node 2: Business Intent Classifier**
   * **Function:** Analyzes the visual and contextual intent of an inbound document payload.
   * **Mechanism:** Dynamically routes the payload into distinct operational queues by classifying it as a **Bulk/Batch Submission** (e.g., multi-row schedule spreadsheets) or a **Standard Processing Submission** (e.g., single-entity application forms).

## 📂 Repository Structure

The application utilizes Streamlit's native Multipage directory routing:

```text
agent-poc/
├── app.py                            # Gateway Dashboard (Home Page)
├── pages/
│   ├── 1_🔍_Structured_Extractor.py  # Agent Node 1: Extraction Logic
│   └── 2_🏢_Intent_Classifier.py     # Agent Node 2: Business Routing Logic
├── .streamlit/
│   └── secrets.toml                  # (Local only) Stores GEMINI_API_KEY
├── .gitignore                        # Excludes secrets from version control
└── requirements.txt                  # Dependency manifest for deployment

Local Development Setup

To run this application on your local machine for testing:

1. Clone the repository:
git clone [https://github.com/Mugil6/agent-poc.git](https://github.com/Mugil6/agent-poc.git)

cd agent-poc

2. Install dependencies:
pip install -r requirements.txt

3. Configure your API Key:
Create a folder named .streamlit in the root directory, and inside it, create a file named secrets.toml.

4. Run the Master Application:

python -m streamlit run app.py






