import streamlit as st
import uuid


st.set_page_config(
    page_title="LegalAI — Legal Assistant",
    page_icon="⚖️",
    layout="wide"
)


st.markdown("""
<style>
.main { background: #0D0E0F; }

.lex-header {
    background: #141618;
    border: 1px solid #2A2D32;
    border-radius: 10px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    border-left: 4px solid #C9A84C;
}
.lex-header h1 { color: #E8E0D0; margin: 0; }
.lex-header p { color: #6B7280; }

.intent-badge {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: bold;
}
.badge-advise { background:#1a2e1a; color:#5FAD89; }
.badge-analyze { background:#1e3a5f; color:#6496C8; }
.badge-draft { background:#2d1f0f; color:#C9A84C; }
.badge-risk { background:#2e1a1a; color:#D95F5F; }
.badge-tool { background:#2d2020; color:#E0A020; }

.source-chip {
    background: #1f2937;
    color: #9CA3AF;
    padding: 2px 6px;
    margin: 2px;
    border-radius: 4px;
    font-size: 0.7rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())[:8]

if "messages" not in st.session_state:
    st.session_state.messages = []

if "meta" not in st.session_state:
    st.session_state.meta = []

with st.sidebar:
    st.title("⚖️ LegalAI")
    st.caption("Legal AI Assistant")

    st.code(f"Session: {st.session_state.thread_id}")

    if st.button("🔄 New Session"):
        st.session_state.thread_id = str(uuid.uuid4())[:8]
        st.session_state.messages = []
        st.session_state.meta = []
        st.rerun()

    st.divider()

    st.markdown("### Try Examples")

    examples = [
        "What is a contract?",
        "Analyze this NDA: unlimited liability and perpetual confidentiality",
        "Draft a 2-year NDA between two companies",
        "Is non-compete enforceable in India?",
        "Score these clauses: unlimited liability, no force majeure",
        "Calculate deadline: start 2026-01-15, 12 months, 30-day notice"
    ]

    for ex in examples:
        if st.button(ex):
            st.session_state._inject = ex
            st.rerun()

st.markdown("""
<div class="lex-header">
<h1>⚖️ LegalAI</h1>
<p>AI-powered Legal Assistant (RAG + Tools + LangGraph)</p>
</div>
""", unsafe_allow_html=True)


for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant" and i//2 < len(st.session_state.meta):
            meta = st.session_state.meta[i//2]

            cols = st.columns([2,2,6])

            with cols[0]:
                badge = meta.get("intent", "advise").replace("tool_", "tool")
                st.markdown(f'<span class="intent-badge badge-{badge}">{badge}</span>', unsafe_allow_html=True)

            with cols[1]:
                st.caption("✅ Pass" if meta.get("eval_passed") else "⚠️ Review")

            with cols[2]:
                sources = meta.get("sources", [])
                if sources:
                    st.markdown(" ".join([f'<span class="source-chip">{s}</span>' for s in sources]), unsafe_allow_html=True)


user_input = st.chat_input("Ask a legal question...")

# Inject example
if "_inject" in st.session_state:
    user_input = st.session_state.pop("_inject")


 
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("⚖️ Processing legal analysis..."):

            try:
                from agent import chat

                result = chat(user_input, thread_id=st.session_state.thread_id)

                response = result.get("response", "No response")

                st.markdown(response)

                # Tool highlights
                if "CONTRACT DEADLINE" in response:
                    st.info("📅 Deadline Analysis Generated")
                elif "RISK" in response:
                    st.warning("⚠️ Risk Assessment Generated")

                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.meta.append(result)

            except Exception as e:
                error = f"⚠️ Error: {str(e)}"
                st.error(error)
                st.session_state.messages.append({"role": "assistant", "content": error})r(error)
                st.session_state.messages.append({"role": "assistant", "content": error})
