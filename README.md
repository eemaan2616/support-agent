# 🛠️ Support Ticket Resolution Agent (LangGraph-Based)

This project is an AI-powered support ticket resolution agent built using **LangGraph**, featuring:
- Graph-based workflow orchestration
- Multi-step review + retry loop
- Escalation logging
- Full LangGraph CLI support


## ✅ Key Features (All Feedback Points Addressed)

- ✅ **Graph-based orchestration** via `StateGraph`  
- ✅ **Modular nodes**: classification, retrieval, generation, review, refine, escalate  
- ✅ **Retry loop with feedback refinement** (up to 2 attempts)  
- ✅ **Conditional routing**: success → end, failure → retry or escalate  
- ✅ **Escalation logging** in `escalation_log.csv` with timestamp & draft  
- ✅ **Proper LangGraph CLI config** (`langgraph.json`)  
- ✅ **LLM-free logic**, easily swappable with LangChain runnables  
- ✅ **Prompt-safe review** (flags refund mentions etc.)

---

## 📁 Project Structure

support-agent/
├── main.py [LangGraph orchestration and nodes]
├── langgraph.json [LangGraph CLI config]
├── requirements.txt [Required Python dependencies]
├── escalation_log.csv [Created at runtime (for escalations)]
└── README.md [This file]


---

## 🚀 Getting Started

### 1. Clone & Set Up
```bash
git clone https://github.com/YOUR_USERNAME/support-agent.git
cd support-agent
python -m venv venv
venv\Scripts\activate   # or source venv/bin/activate on Mac/Linux
pip install -r requirements.txt

### 2. Run from CLI
python main.py

### OR Could be Run from LangGraph CLI
npm install -g langgraph
langgraph dev


## ARCHITECTURE 
classify_ticket
      ↓
retrieve_context
      ↓
generate_draft
      ↓
review_response
   ↙       ↘
refine_context   escalate_ticket
   ↓
generate_draft (retry)


### LOG FORMAT
timestamp,subject,category,attempts,draft
2025-07-16T18:12:43,Payment failed on checkout,Billing,2,"Hi there, ..."


### SAMPLE OUTPUT
🔁 Retry attempt #1
❌ Max attempts reached. Escalating to human agent.
📁 Logged to escalation_log.csv

=== Final Draft ===

Hi there,
Thanks for reaching out regarding: Payment failed on checkout
...

=== Review Feedback ===
❌ Policy violation: mentions 'refund'
✅ Approved? False
🔁 Attempts: 2




# CREATED BY :EEMAAN AHMAD

