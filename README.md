# 📄 AI ACORD Underwriting Extractor (Agentic PoC)

An enterprise-grade Proof of Concept (PoC) demonstrating agentic ingestion and structured data extraction from complex, tabular ACORD insurance documents using multimodal Large Language Models (LLMs). Access the app here - https://agent-poc-wpuhau5hlgpqlus8qyv5jq.streamlit.app/

## 🎯 Architecture Overview

This repository houses the rapid-prototyping architecture for the Underwriting Extraction Agent. 
* **Current State (PoC):** Built using Streamlit and Google's Gemini 2.5 Flash API to demonstrate immediate capability, multimodal vision parsing, and strict JSON schema enforcement (via Pydantic) without requiring local AWS infrastructure.
* **Target State (Production):** The core extraction logic and Pydantic schemas are designed to be entirely decoupled from the UI. For production deployment, this logic will be migrated to the **AWS AgentCore** framework and executed via **Amazon Bedrock** to ensure strict VPC isolation, zero data retention, and enterprise compliance.

## ✨ Features
* **Multimodal Vision Parsing:** Bypasses traditional OCR by using native vision-language models to understand spatial layouts, grids, and nested tables in ACORD documents.
* **Strict Schema Enforcement:** Utilizes `Pydantic` to guarantee that the LLM outputs exact, strongly-typed JSON relationships mapping Policies, Limits, and Carriers.
* **Dynamic Error Handling:** Intelligent prompt engineering instructs the agent to flag unreadable or missing fields explicitly, preventing silent hallucinations.

## 🚀 Local Development Setup

Follow these steps to run the agent locally on your machine.

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your system.

### 2. Install Dependencies
Clone this repository and install the required Python packages:
```bash
git clone [https://github.com/Mugil6/agent-poc.git](https://github.com/Mugil6/agent-poc.git)
cd agent-poc

pip install -r requirements.txt


### 3. Run the application
python -m streamlit run app.py


