# 🛠️ Support Ticket Resolution Agent (LangGraph)

An AI-powered multi-step support assistant built using [LangGraph](https://langchain-ai.github.io/langgraph/). It classifies, retrieves context, drafts, and reviews support replies — with retry loops and escalation.

---

## 📌 Features

- ✅ Accepts support tickets (`subject`, `description`)
- 🧠 Classifies into: Billing, Technical, Security, or General
- 🔍 Retrieves relevant info from a mock knowledge base (simulated RAG)
- ✍ Generates a response draft
- ✅ Reviews the draft for policy compliance (mock reviewer)
- 🔁 Retries up to 2 times if the draft is rejected
- 📁 Escalates failed tickets into a CSV file for manual triage

---

## 🧱 Project Structure

support-agent/
│
├── main.py # Main LangGraph agent logic
├── escalation_log.csv # (Optional) Failed tickets for manual review
└── README.md # You're here!


---

## 🧪 How to Run

### 1. Setup Environment

```bash
git clone https://github.com/your-username/support-agent.git
cd support-agent
python -m venv venv
venv\\Scripts\\activate         # Windows
# or
source venv/bin/activate       # Mac/Linux

### 2. Install Dependencies

pip install -r requirements.txt
# OR install manually:
pip install langgraph langchain openai tiktoken

### 3. Run the Agent
python main.py


