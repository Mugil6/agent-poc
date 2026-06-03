# 🛡️ Agentic AI: Intelligent Intake & Orchestration Portal (PoC)

This repository contains a Proof of Concept (PoC) for an **Enterprise Multi-Agent Orchestration Pipeline**. It is designed to automate the ingestion, structural extraction, intent classification, and system-of-record synthesis for complex business documents.

Built with **Streamlit's Multipage Architecture**, **Pydantic**, and the **Native Gemini API**, this application demonstrates how multimodal Large Language Models (LLMs) can act as deterministic reasoning nodes, moving beyond text generation to execute stateful business workflows.

## 🏗️ Architecture: PoC vs. Production

This repository serves as **Phase 1 (Local/Cloud Demo)** to validate agentic reasoning and data extraction capabilities without requiring enterprise infrastructure overhead.

* **Phase 1 (Current PoC):** Utilizes `google.generativeai` (Gemini 2.5 Flash open weights) and Streamlit Community Cloud. This allows stakeholders to interact with the UI, test sample documents, and validate end-to-end extraction and routing accuracy.
* **Phase 2 (Target Enterprise Architecture):** The logic, prompt engineering, and strict Pydantic schemas built here are highly modular. Upon securing cloud provisioning, these Streamlit pages will be decoupled, wrapped in scalable agent SDKs (such as AWS AgentCore or similar frameworks), and deployed as isolated serverless functions within a secure VPC.

## 🧠 The Agent Nodes

This portal is structured as a Microservices Architecture. Each "Page" represents a distinct AI Agent with a specific operational capability:

1. **🔍 Node 1: Structured Data Extractor (The Data Specialist)**
   * **Function:** Navigates complex grid layouts and tabular formats inherent to standardized industry forms.
   * **Mechanism:** Enforces strict `Pydantic` schemas to force the LLM to output highly nested, deterministic JSON (mapping entity details, identification codes, and quantitative metrics).
2. **🏢 Node 2: Business Intent Classifier (The Business Analyst)**
   * **Function:** Analyzes the visual and contextual intent of an inbound document payload.
   * **Mechanism:** Dynamically classifies the payload into distinct operational pathways (e.g., distinguishing between a **Bulk/Batch Submission** versus a **Standard Single-Entity Submission**).
3. **📝 Node 3: Case Creation Agent (The System Integrator)**
   * **Function:** Acts as the final workflow orchestrator and "Human-in-the-loop" safeguard.
   * **Mechanism:** Takes the output from Node 1 and Node 2, assesses data completeness, determines SLA priority, and generates a formatted JSON API payload ready for downstream CRM/ERP injection. It automatically flags missing structural anomalies (e.g., missing identification codes) and routes incomplete cases to an Exceptions Desk.

## 📂 Repository Structure

The application utilizes Streamlit's native Multipage directory routing:

```text
agent-poc/
├── app.py                            # Gateway Dashboard (Home Page)
├── pages/
│   ├── 1_🔍_Structured_Extractor.py  # Agent Node 1: Extraction Logic
│   ├── 2_🏢_Intent_Classifier.py     # Agent Node 2: Business Routing Logic
│   └── 3_📝_Case_Creator.py          # Agent Node 3: End-to-End Orchestration
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


3. Run the Master Application:
Execute the root file. Streamlit will automatically detect the pages/ folder and build the sidebar navigation.
Bash

python -m streamlit run app.py

☁️ Deployment (Streamlit Community Cloud)

To deploy this unified portal for a live demonstration:

    Ensure your .streamlit/secrets.toml file is not pushed to GitHub (check your .gitignore).

    Log into Streamlit Community Cloud using your GitHub account.

    Click New app and select your repository.

    Set the Main file path to app.py.

    Click Advanced Settings -> Secrets and paste your API key exactly as it appears locally:
    Ini, TOML

    GEMINI_API_KEY="your-api-key-here"

    Click Deploy.

⚠️ Compliance & Security Warning

This PoC currently routes data through public LLM endpoints for rapid prototyping and demonstration purposes. Do not upload documents containing real Personally Identifiable Information (PII) or sensitive organizational data to this portal. Please use publicly available, sanitized, or dummy documents for all testing and demonstrations until a secure cloud infrastructure is fully implemented.



Copyright (c) 2026 [Mugilan]. All Rights Reserved.