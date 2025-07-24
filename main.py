from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from dataclasses import dataclass, replace
from typing import Optional
from datetime import datetime
import csv

# ✅ LangGraph-compatible state object
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

# ✅ Classification node
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
    return replace(state, category=category)

# ✅ RAG simulation (static context per category)
category_context = {
    "Billing": "Check if the payment method is valid.",
    "Technical": "Try restarting the app and clearing the cache.",
    "Security": "Reset your password and enable 2FA.",
    "General": "Please provide more information about your issue.",
}

def retrieve_context(state: TicketState) -> TicketState:
    context = category_context.get(state.category, "We're looking into this.")
    return replace(state, context=context)

# ✅ Draft generation
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
    return replace(state, draft=draft)

# ✅ Review logic
def review_response(state: TicketState) -> TicketState:
    draft_lower = state.draft.lower() if state.draft else ""
    feedback = ""
    approved = True

    if "refund" in draft_lower:
        feedback = "❌ Policy violation: Draft mentions 'refund'. Support agents are not allowed to offer refunds directly."
        approved = False
    elif len(state.draft or "") < 30:
        feedback = "❌ Draft too short and not helpful."
        approved = False
    else:
        feedback = "✅ Response looks good."

    return replace(state, feedback=feedback, approved=approved)

# ✅ Escalation logger
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

# ✅ Conditional routing
def route_based_on_review(state: TicketState) -> str:
    if state.approved:
        return "end"
    elif state.attempts >= 2:
        return "escalate"
    else:
        return "refine_context"

# ✅ Retry with context refinement
def refine_context(state: TicketState) -> TicketState:
    updated_context = state.context
    if state.category == "Billing":
        updated_context += " Please contact billing support for refunds."
    return replace(state, context=updated_context, attempts=state.attempts + 1)

# ✅ LangGraph definition
builder = StateGraph(TicketState)

builder.add_node("classify_ticket", RunnableLambda(classify_ticket))
builder.add_node("retrieve_context", RunnableLambda(retrieve_context))
builder.add_node("generate_draft", RunnableLambda(generate_draft))
builder.add_node("review_response", RunnableLambda(review_response))
builder.add_node("refine_context", RunnableLambda(refine_context))
builder.add_node("escalate", RunnableLambda(escalate_to_csv))

builder.set_entry_point("classify_ticket")
builder.add_edge("classify_ticket", "retrieve_context")
builder.add_edge("retrieve_context", "generate_draft")
builder.add_edge("generate_draft", "review_response")
builder.add_conditional_edges("review_response", route_based_on_review, {
    "end": END,
    "refine_context": "generate_draft",
    "escalate": "escalate"
})

app = builder.compile()

# ✅ Run the graph
if __name__ == "__main__":
    input_state = TicketState(
        subject="Payment failed on checkout",
        description="I tried to pay with my card but it didn’t go through."
    )

    final_state = app.invoke(input_state)

    print("\n=== Final Draft ===\n")
    print(final_state["draft"])

    print("\n=== Review Feedback ===\n")
    print(final_state["feedback"])

    print(f"\n✅ Approved? {final_state['approved']}")
    print(f"🔁 Attempts: {final_state['attempts']}")
