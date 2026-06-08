🛡️ Enterprise P&C Underwriting OS

An asynchronous, multi-agent AI underwriting pipeline built with Streamlit and Google Gemini (3.1 Flash-Lite). This system orchestrates 10 specialized AI micro-agents using a Hierarchical Supervisor Pattern to process broker submissions, assess risk, generate actuarial pricing, and draft broker communications safely within API limits.

🏗️ Architecture Overview

The pipeline transitions from a monolithic manual workflow to an automated Master Agent (Supervisor) architecture. It is divided into three core phases:

1️⃣ Intake Master (pages/📥_Intake_Master.py)

Orchestrates Nodes 1-4 to handle high-volume structural tasks.

Node 1 (Extractor): Parses deep tabular data (Policies, Limits, Carriers) from uploaded ACORD forms using JSON schemas.

Node 2 (Classifier): Visually determines business intent (e.g., Bookroll vs. New Business).

Node 3 (Case Creator): Synthesizes extracted data into a structured CRM payload.

Node 4 (Exception): Automatically drafts broker emails if mandatory data is missing.

2️⃣ Assess Master (pages/📊_Assess_Master.py)

Orchestrates Nodes 5-8 to handle high-risk reasoning and financial liability.

Node 5 (Enrichment): Simulates fetching external geographic and compliance hazard data.

Node 6 (Rating Engine): Applies actuarial reasoning to calculate base premiums and hazard multipliers.

Node 7 (UW Summary): Synthesizes risk nuances into an Executive Decision Support summary.

Node 8 (Quote Prep): Formats approved rating data into a formal, structured quote document.

3️⃣ Bind Master (pages/🤝_Bind_Master.py)

Orchestrates Nodes 9-10 to handle sales strategy and dispatch.

Node 9 (Cross-Sell): Dynamically generates a portfolio of logical upsell products tailored to the exact risk profile.

Node 10 (Issuance): Uses raw text generation to draft a persuasive, long-form dispatch email to the broker (bypassing JSON token limitations).

🚀 Key Technical Features

Pydantic Schema Enforcement: Guarantees structural integrity of LLM outputs for seamless data handoffs between agents.

API Latency & Quota Pacing: Utilizes strategic time.sleep() injections between agent calls to prevent 429 Quota Exhausted errors on free-tier APIs (15 Requests Per Minute limit).

Decoupled State Rendering: Separates AI execution logic from Streamlit UI rendering to prevent screen flashing and NoneType tracebacks.

Hybrid Output Generation: Uses strict JSON mode for data extraction (Nodes 1-9) and Raw Text mode for long-form creative generation (Node 10) to prevent token truncation.

🛠️ Setup & Installation

1. Prerequisites

Ensure you have Python 3.9+ installed.

pip install streamlit google-generativeai pydantic pandas


2. API Key Configuration

Create a .streamlit folder in the root directory and add a secrets.toml file to securely store your Google Gemini API key.

.streamlit/secrets.toml

GEMINI_API_KEY = "your_google_ai_studio_api_key"


3. Run the Application

Launch the master gateway from your terminal:

python -m streamlit run app.py


📂 Project Structure
```text
agent-poc/
├── .streamlit/
│   └── secrets.toml                    # API Keys (Do not commit to GitHub)
├── app.py                              # Global Upload & Dashboard Overview
├── pages/
│   ├── 1_📥_Intake_Master.py           # Runs Nodes 1, 2, 3, 4 automatically
│   ├── 2_📊_Assess_Master.py           # Runs Nodes 5, 6, 7, 8 automatically
│   └── 3_🤝_Bind_Master.py             # Runs Nodes 9, 10 automatically
└── README.md


📝 Future Enterprise Upgrades (Roadmap)

AgentCore & MCP Migration: Transition from hardcoded simulated enrichment (Node 5) to live database queries using the Model Context Protocol (MCP) and AWS Bedrock.

Asynchronous Processing: Move execution from Streamlit frontend loops to AWS EventBridge / Celery background workers.

📜 License

Copyright (c) 2026 Mugilan. All Rights Reserved.