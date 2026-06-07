# 🛡️ Agentic AI: P&C Underwriting Operating System (PoC)

This repository contains a Proof of Concept (PoC) for an **Enterprise Multi-Agent Underwriting Pipeline**. It automates the entire lifecycle from document ingestion and triage to risk assessment, premium rating, and broker dispatch.

Built with **Streamlit** and the **Native Gemini API**, this application demonstrates a decoupled micro-agent architecture. By separating tasks into standalone nodes passing data via global memory, it ensures modularity, fault tolerance, and enterprise-grade scalability.

## 🏗️ The 3-Stage Pipeline (10 Agent Nodes)

### Stage 1: Intake & Triage
1. **🔍 Node 1: Extractor:** Parses complex grids/tables into structured DataFrames.
2. **🏢 Node 2: Classifier:** Analyzes visual structure to determine business intent (e.g., Bookroll vs. New Business).
3. **📝 Node 3: Case Creator:** Synthesizes outputs into a clean CRM ticket.
4. **📧 Node 4: Exception Agent:** Automatically drafts broker emails to request missing data.

### Stage 2: Quote & Assess
5. **🌐 Node 5: Enrichment:** Fetches external geographical and compliance risk data.
6. **🧮 Node 6: Rating:** Calculates premium based on hazard multipliers.
7. **⚖️ Node 7: Summarization:** Provides an executive summary for human underwriting decision support.
8. **📄 Node 8: Quote Prep:** Drafts the formal quote document and subjectivities.

### Stage 3: Negotiate & Bind
9. **📈 Node 9: Cross-Sell:** Runs predictive models to suggest logical upsell products.
10. **✉️ Node 10: Issuance:** Synthesizes the quote and upsell opportunities into a final dispatch communication.

## 📂 Repository Structure
```text
agent-poc/
├── app.py                              # Global Upload & Master Orchestrator
├── pages/
│   ├── 1_🔍_Structured_Extractor.py    
│   ├── 2_🏢_Intent_Classifier.py       
│   ├── 3_📝_Case_Creator.py            
│   ├── 4_📧_Exception_Communicator.py  
│   ├── 5_🌐_Enrichment_Agent.py        
│   ├── 6_🧮_Rating_Agent.py            
│   ├── 7_⚖️_Summarization_Agent.py     
│   ├── 8_📄_Quote_Prep_Agent.py        
│   ├── 9_📈_Cross_Sell_Agent.py        
│   └── 10_✉️_Issuance_Agent.py         
├── .streamlit/
│   └── secrets.toml                  # Stores GEMINI_API_KEY
└── requirements.txt                  # Dependency manifest

 Local Development

    Clone the repository and pip install -r requirements.txt.

    Configure .streamlit/secrets.toml with your API Key.

    Run python -m streamlit run app.py. Upload a document to the Global Memory bank to execute the pipeline.

   Copyright (c) 2026 [Mugilan]. All Rights Reserved.