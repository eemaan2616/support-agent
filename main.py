from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage
from dataclasses import dataclass
from typing import TypedDict, List, Optional
from datetime import datetime
import csv

# ✅ Required for LangGraph State Tracking
@dataclass
class TicketState:
    subject: str
    description: str
    category: Optional[str] = None
    context: Optional[str] = None
    draft: Optional[str] = None
    feedback: Optional[str] = None
    approved: Optional[bool] = None
    attempts: int = 0

# ✅ Classification Node
def classify_ticket(state: TicketState) -> TicketState:
    text = (state.subject + " " + state.description).lower()
    if "payment" in text or "card" in text:
        category = "Billing"
    elif "error" in text or "bug" in text:
        category = "Technical"
    elif "password" in text or "hacked" in text:
        category = "Security"
    else:
        category = "General"
    return TicketState(**state.__dict__, category=category)

# ✅ Simulated RAG Node (can be extended later)
category_context = {
    "Billing": "Check if the payment method is valid.",
    "Technical": "Try restarting the app and clearing the cache.",
    "Security": "Reset your password and enable 2FA.",
    "General": "Please provide more information about your issue.",
}

def retrieve_context(state: TicketState) -> TicketState:
    context = category_context.get(state.category, "We're looking into this.")
    return TicketState(**state.__dict__, context=context)

# ✅ Draft Generation Node
def generate_draft(state: TicketState) -> TicketState:
    draft = f"""
Hi there,

Thanks for reaching out regarding: {state.subject}
We understand your concern: "{state.description}"

Based on our knowledge, here are some suggestions:
{state.context}

If the issue persists, feel free to contact us again.

Best regards,
Support Team
""".strip()
    return TicketState(**state.__dict__, draft=draft)

# ✅ Review Node with Feedback
def review_response(state: TicketState) -> TicketState:
    feedback = ""
    approved = True

    if "refund" in state.draft.lower():
        feedback = "❌ Policy violation: Draft mentions 'refund'. Support agents are not allowed to offer refunds directly."
        approved = False

    elif len(state.draft) < 30:
        feedback = "❌ Draft too short and not helpful."
        approved = False

    else:
        feedback = "✅ Response looks good."

    return TicketState(**state.__dict__, feedback=feedback, approved=approved)

# ✅ Escalation Logger (runs only on final failure)
def escalate_to_csv(state: TicketState) -> TicketState:
    with open("escalation_log.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now(),
            state.subject,
            state.description,
            state.category,
            state.draft,
            state.feedback
        ])
    print("📁 Logged to escalation_log.csv")
    return state

# ✅ Conditional Router
def route_based_on_review(state: TicketState) -> str:
    if state.approved:
        return "end"
    elif state.attempts >= 2:
        return "escalate"
    else:
        return "refine_context"

# ✅ Context Refinement Node (retry path)
def refine_context(state: TicketState) -> TicketState:
    # Improve or reword the context slightly
    context = state.context + " Please contact billing support for refunds." if state.category == "Billing" else state.context
    return TicketState(**state.__dict__, context=context, attempts=state.attempts + 1)

# ✅ Build the Graph
builder = StateGraph(TicketState)

builder.add_node("classify_ticket", RunnableLambda(classify_ticket))
builder.add_node("retrieve_context", RunnableLambda(retrieve_context))
builder.add_node("generate_draft", RunnableLambda(generate_draft))
builder.add_node("review_response", RunnableLambda(review_response))
builder.add_node("refine_context", RunnableLambda(refine_context))
builder.add_node("escalate", RunnableLambda(escalate_to_csv))

# ✅ Set Entry Point
builder.set_entry_point("classify_ticket")

# ✅ Define Edges
builder.add_edge("classify_ticket", "retrieve_context")
builder.add_edge("retrieve_context", "generate_draft")
builder.add_edge("generate_draft", "review_response")

# ✅ Conditional Branching (review outcome)
builder.add_conditional_edges("review_response", route_based_on_review, {
    "end": END,
    "refine_context": "generate_draft",
    "escalate": "escalate"
})

# ✅ Compile the app (for CLI or Python execution)
app = builder.compile()

# === Test Run ===
if __name__ == "__main__":
    input_state = TicketState(
        subject="Payment failed on checkout",
        description="I tried to pay with my card but it didn’t go through."
    )

    final_state = app.invoke(input_state)

    print("\n=== Final Draft ===\n")
    print(final_state.draft)

    print("\n=== Review Feedback ===\n")
    print(final_state.feedback)

    print(f"\n✅ Approved? {final_state.approved}")
    print(f"🔁 Attempts: {final_state.attempts}")
