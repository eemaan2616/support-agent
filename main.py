from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal
import csv
import os

# 1. Ticket categories
CATEGORIES = ["Billing", "Technical", "Security", "General"]

# 2. State definition
class TicketInput(TypedDict):
    subject: str
    description: str

class TicketState(TypedDict):
    ticket: TicketInput
    category: Literal["Billing", "Technical", "Security", "General"] | None
    docs: list[str]
    draft: str
    approved: bool
    review_feedback: str
    attempts: int
    all_drafts: list[str]
    all_feedback: list[str]

# 3. Classifier
def classify_ticket(state: TicketState) -> TicketState:
    subject = state["ticket"]["subject"].lower()
    description = state["ticket"]["description"].lower()

    if "payment" in subject or "invoice" in description:
        category = "Billing"
    elif "error" in description or "bug" in subject:
        category = "Technical"
    elif "hacked" in description or "breach" in subject:
        category = "Security"
    else:
        category = "General"

    return {**state, "category": category}

# 4. Fake knowledge base
KNOWLEDGE_BASE = {
    "Billing": [
        "Check if the payment method is valid.",
        "Please contact billing support for refunds."
    ],
    "Technical": [
        "Clear your browser cache.",
        "Try updating the app."
    ],
    "Security": [
        "Reset your password immediately.",
        "Enable 2FA for better protection."
    ],
    "General": [
        "Thank you for contacting support.",
        "We'll get back to you soon."
    ]
}

# 5. Context Retrieval
def retrieve_context(state: TicketState) -> TicketState:
    category = state["category"]
    docs = KNOWLEDGE_BASE.get(category, [])
    return {**state, "docs": docs}

# 6. Draft Generator
def generate_draft(state: TicketState) -> TicketState:
    subject = state["ticket"]["subject"]
    description = state["ticket"]["description"]
    docs = state.get("docs", [])

    context = "\n".join(docs)
    draft = (
        f"Hi there,\n\n"
        f"Thanks for reaching out regarding: {subject}\n"
        f"We understand your concern: \"{description}\"\n\n"
        f"Based on our knowledge, here are some suggestions:\n"
        f"{context}\n\n"
        f"If the issue persists, feel free to contact us again.\n\n"
        f"Best regards,\nSupport Team"
    )

    state["draft"] = draft
    state["all_drafts"].append(draft)
    return state

# 7. Reviewer
def review_draft(state: TicketState) -> TicketState:
    draft = state["draft"]
    approved = True
    feedback = ""

    if "refund" in draft.lower():
        approved = False
        feedback = (
            "❌ Policy violation: Draft mentions 'refund'. "
            "Support agents are not allowed to offer refunds directly."
        )
    else:
        feedback = "✅ Draft approved."

    state["review_feedback"] = feedback
    state["approved"] = approved
    state["attempts"] += 1
    state["all_feedback"].append(feedback)
    return state

# 8. Log escalation
def escalate(state: TicketState):
    file_path = "escalation_log.csv"
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Subject", "Description", "Category", "Attempts",
                "Drafts", "Feedback"
            ])

        writer.writerow([
            state["ticket"]["subject"],
            state["ticket"]["description"],
            state["category"],
            state["attempts"],
            "\n---\n".join(state["all_drafts"]),
            "\n---\n".join(state["all_feedback"])
        ])

    print("📁 Logged to escalation_log.csv")

# 9. Retry Decision Logic
def decide_next_step(state: TicketState) -> str:
    if state["approved"]:
        return END
    elif state["attempts"] >= 2:
        print("❌ Max attempts reached. Escalating to human agent.")
        escalate(state)
        return END
    else:
        print(f"🔁 Retry attempt #{state['attempts']}")
        return "retrieve_context"

# 10. Build the graph
workflow = StateGraph(TicketState)

workflow.add_node("classify", classify_ticket)
workflow.add_node("retrieve_context", retrieve_context)
workflow.add_node("generate_draft", generate_draft)
workflow.add_node("review_draft", review_draft)

workflow.set_entry_point("classify")
workflow.add_edge("classify", "retrieve_context")
workflow.add_edge("retrieve_context", "generate_draft")
workflow.add_edge("generate_draft", "review_draft")
workflow.add_conditional_edges("review_draft", decide_next_step, {
    END: END,
    "retrieve_context": "retrieve_context"
})

app = workflow.compile()

# 11. Run a test
if __name__ == "__main__":
    test_input = {
        "ticket": {
            "subject": "Payment failed on checkout",
            "description": "I tried to pay with my card but it didn’t go through."
        },
        "category": None,
        "docs": [],
        "draft": "",
        "approved": False,
        "review_feedback": "",
        "attempts": 0,
        "all_drafts": [],
        "all_feedback": []
    }

    result = app.invoke(test_input)

    print("\n=== Final Draft ===\n")
    print(result["draft"])
    print("\n=== Review Feedback ===\n")
    print(result["review_feedback"])
    print(f"\n✅ Approved? {result['approved']}")
    print(f"🔁 Attempts: {result['attempts']}")
