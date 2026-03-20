import os
import sys
import time
import asyncio
import datetime
import streamlit as st
from dotenv import load_dotenv

if sys.platform == "win32":
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

# Page Config (MUST be first Streamlit call)
st.set_page_config(
    page_title="GitBot — GitLab AI Assistant",
    page_icon="🦊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
    color: #e6edf3;
}

/* ── Header ── */
.main-header {
    background: linear-gradient(90deg, #fc6d26 0%, #e24329 40%, #fca326 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.4rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}
.sub-header {
    color: #7d8590;
    font-size: 0.95rem;
    margin-top: -8px;
    margin-bottom: 20px;
}

/* ── Chat messages ── */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 10px 0;
}
.user-message {
    display: flex;
    justify-content: flex-end;
    animation: slideInRight 0.3s ease;
}
.user-bubble {
    background: linear-gradient(135deg, #fc6d26, #e24329);
    color: white;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    max-width: 75%;
    font-size: 0.95rem;
    line-height: 1.5;
    box-shadow: 0 4px 15px rgba(252, 109, 38, 0.3);
}
.bot-message {
    display: flex;
    justify-content: flex-start;
    animation: slideInLeft 0.3s ease;
    gap: 12px;
}
.bot-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #1c2128, #fc6d26);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
    border: 2px solid #fc6d26;
}
.bot-bubble {
    background: #1c2128;
    border: 1px solid #30363d;
    color: #e6edf3;
    padding: 14px 18px;
    border-radius: 4px 18px 18px 18px;
    max-width: 80%;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

/* ── Confidence Badge ── */
.confidence-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-top: 8px;
    letter-spacing: 0.5px;
}
.badge-high   { background: #1a4731; color: #3fb950; border: 1px solid #238636; }
.badge-medium { background: #3d2f1e; color: #d29922; border: 1px solid #9e6a03; }
.badge-low    { background: #3d1c1c; color: #f85149; border: 1px solid #da3633; }

/* ── Token usage ── */
.token-info {
    font-size: 0.72rem;
    color: #484f58;
    margin-top: 6px;
}

/* ── Guardrail warning ── */
.guardrail-msg {
    background: #2d1f1a;
    border: 1px solid #da3633;
    border-left: 4px solid #f85149;
    border-radius: 8px;
    padding: 12px 16px;
    color: #f85149;
    font-size: 0.9rem;
    margin: 8px 0;
}

/* ── Suggested questions ── */
.suggestion-btn {
    background: #1c2128 !important;
    border: 1px solid #30363d !important;
    color: #58a6ff !important;
    border-radius: 20px !important;
    font-size: 0.85rem !important;
    padding: 6px 14px !important;
    transition: all 0.2s ease !important;
}
.suggestion-btn:hover {
    border-color: #fc6d26 !important;
    color: #fc6d26 !important;
    background: #21262d !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #161b22 !important;
    border-right: 1px solid #30363d;
}
[data-testid="stSidebar"] .stMarkdown {
    color: #e6edf3;
}

/* ── Divider ── */
.section-divider {
    border: none;
    border-top: 1px solid #21262d;
    margin: 16px 0;
}

/* ── Status indicator ── */
.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-green { background: #3fb950; box-shadow: 0 0 6px #3fb950; }
.status-red   { background: #f85149; box-shadow: 0 0 6px #f85149; }
.status-yellow{ background: #d29922; box-shadow: 0 0 6px #d29922; }

/* ── Input box ── */
.stChatInput > div {
    background: #1c2128 !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
}
.stChatInput input {
    color: #e6edf3 !important;
}

/* ── Animations ── */
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(20px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-20px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}
.typing-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #fc6d26;
    border-radius: 50%;
    animation: pulse 1.2s infinite;
    margin: 0 2px;
}
.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

/* ── Source card ── */
.source-card {
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.82rem;
}
.source-card a { color: #58a6ff; text-decoration: none; }
.source-card a:hover { text-decoration: underline; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #484f58; }

/* Override default white Streamlit elements */
.stTextInput > div > div {
    background: #1c2128;
    border-color: #30363d;
    color: #e6edf3;
}
div[data-testid="stExpander"] {
    background: #1c2128;
    border: 1px solid #30363d;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)


# Session Initialisation
def init_session():
    defaults = {
        "messages":        [],    # {role, content, sources, confidence, tokens, timestamp}
        "retriever":       None,
        "index_ready":     False,
        "top_k":           5,
        "temperature":     0.3,
        "show_sources":    True,
        "show_tokens":     True,
        "pending_query":   None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# Load Retriever (cached)
@st.cache_resource(show_spinner=False)
def load_retriever():
    """Load the FAISS or Supabase retriever once and cache it."""
    from src.retriever import Retriever
    r = Retriever()
    r._load()
    return r

def check_index_ready() -> bool:
    from src.embeddings import index_exists
    return index_exists()


def format_timestamp() -> str:
    return datetime.datetime.now().strftime("%H:%M")

def render_confidence_badge(confidence: dict) -> str:
    label = confidence.get("label", "Low")
    score = confidence.get("score", 0)
    css   = {"High": "badge-high", "Medium": "badge-medium", "Low": "badge-low"}
    icon  = {"High": "●", "Medium": "◑", "Low": "○"}
    return (
        f'<span class="confidence-badge {css.get(label, "badge-low")}">'
        f'{icon.get(label,"○")} {label} Confidence ({score:.0%})'
        f'</span>'
    )


def export_chat() -> str:
    lines = [f"GitBot — Chat Export — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
    lines.append("=" * 60)
    for msg in st.session_state.messages:
        role = "You" if msg["role"] == "user" else "GitBot"
        ts   = msg.get("timestamp", "")
        lines.append(f"\n[{ts}] {role}:")
        lines.append(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            lines.append("\nSources:")
            for s in msg["sources"]:
                lines.append(f"  - {s['title']}: {s['url']}")
    return "\n".join(lines)


SUGGESTED_QUESTIONS = [
    "What are GitLab's core values?",
    "How does GitLab handle asynchronous communication?",
    "What is GitLab's product direction for CI/CD?",
    "How does the GitLab hiring process work?",
    "What does 'Iteration' mean at GitLab?",
    "How does GitLab approach remote work?",
    "What is GitLab's vision for DevSecOps?",
    "How does GitLab handle performance reviews?",
]


# Sidebar
with st.sidebar:
    st.markdown("## 🦊 GitBot")
    st.markdown("*AI Assistant for GitLab Handbook & Direction*")
    st.markdown("---")

    # Index status
    st.markdown("### 📊 Data Status")
    if check_index_ready():
        st.markdown(
            '<span class="status-dot status-green"></span> **Index Ready**',
            unsafe_allow_html=True,
        )
        st.session_state.index_ready = True
        try:
            if st.session_state.retriever is None:
                with st.spinner("Loading knowledge base..."):
                    st.session_state.retriever = load_retriever()
            chunk_count = (
                st.session_state.retriever._collection.count()
                if st.session_state.retriever._collection
                else "N/A"
            )
            st.caption(f"📚 {chunk_count} knowledge chunks loaded")
        except Exception as e:
            st.caption(f"⚠️ Retriever error: {e}")
    else:
        st.markdown(
            '<span class="status-dot status-red"></span> **Index Not Built**',
            unsafe_allow_html=True,
        )
        st.info(
            "Run the indexer first:\n```bash\npython scripts/build_index.py\n```",
        )
        st.session_state.index_ready = False

    st.caption("🗄 Backend: ChromaDB")

    st.markdown("---")

    # Settings
    st.markdown("### ⚙️ Settings")
    st.session_state.top_k = st.slider(
        "Sources per answer (Top-K)",
        min_value=1, max_value=10, value=st.session_state.top_k,
        help="How many source chunks to retrieve for each answer",
    )
    st.session_state.temperature = st.slider(
        "Response creativity",
        min_value=0.0, max_value=1.0, value=st.session_state.temperature, step=0.1,
        help="Lower = more factual, Higher = more creative",
    )
    st.session_state.show_sources = st.toggle("Show source citations", value=st.session_state.show_sources)
    st.session_state.show_tokens  = st.toggle("Show token usage", value=st.session_state.show_tokens)

    st.markdown("---")

    # About
    st.markdown("### ℹ️ About")
    st.markdown("""
**GitBot** uses Retrieval-Augmented Generation (RAG) to answer questions grounded in GitLab's official content.

**Data Sources:**
- 📖 [GitLab Handbook](https://handbook.gitlab.com)
- 🗺 [GitLab Direction](https://about.gitlab.com/direction)
**Stack:** Gemini 2.5 Flash + ChromaDB + Streamlit
    """)

    st.markdown("---")

    # Export
    if st.session_state.messages:
        export_data = export_chat()
        st.download_button(
            label="💾 Export Chat",
            data=export_data,
            file_name=f"gitbot_chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
        )
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


# Main Area

# Header
st.markdown('<div class="main-header">🦊 GitBot</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Your AI-powered guide to GitLab\'s Handbook & Product Direction</div>',
    unsafe_allow_html=True,
)

# Suggested Questions (only when chat is empty)
if not st.session_state.messages:
    st.markdown("#### 💡 Try asking:")
    cols = st.columns(2)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 2]:
            if st.button(q, key=f"sugg_{i}", use_container_width=True):
                st.session_state.pending_query = q

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

# Chat History
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="user-message">'
            f'  <div class="user-bubble">{msg["content"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        ts = msg.get("timestamp", "")
        conf = msg.get("confidence", {})
        tokens = msg.get("tokens", {})
        sources = msg.get("sources", [])

        badge_html = render_confidence_badge(conf) if conf else ""
        token_html = ""
        if st.session_state.show_tokens and tokens:
            tp = tokens.get("prompt_tokens", 0)
            to = tokens.get("output_tokens", 0)
            token_html = f'<div class="token-info">🔢 Tokens — Prompt: {tp} | Output: {to}</div>'

        st.markdown(
            f'''<div class="bot-message">
                <div class="bot-avatar">🦊</div>
                <div class="bot-bubble">''', 
            unsafe_allow_html=True
        )
        
        st.markdown(msg["content"])
        
        st.markdown(
            f'''{badge_html}
                {token_html}
                </div>
            </div>''', 
            unsafe_allow_html=True
        )

        # Sources accordion
        if st.session_state.show_sources and sources:
            with st.expander(f"📚 {len(sources)} Sources Used", expanded=False):
                for i, src in enumerate(sources, 1):
                    sim = src.get("similarity", 0)
                    text_preview = src.get("text", "")[:280].replace("\n", " ")
                    st.markdown(
                        f'<div class="source-card">'
                        f'  <strong>Source {i}</strong> · '
                        f'  <a href="{src["url"]}" target="_blank">{src["title"] or src["url"]}</a>'
                        f'  <span style="float:right; color:#484f58">Relevance: {sim:.0%}</span>'
                        f'  <br><span style="color:#7d8590">{text_preview}…</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

# Show suggested follow-up questions exclusively for the VERY LAST assistant message
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    last_msg = st.session_state.messages[-1]
    if suggs := last_msg.get("suggested_questions"):
        st.markdown("#### 🤔 Follow-up Questions:")
        cols = st.columns(len(suggs))
        for i, sq in enumerate(suggs):
            with cols[i]:
                btn_key = f"followup_{len(st.session_state.messages)}_{i}"
                if st.button(sq, key=btn_key, use_container_width=True):
                    st.session_state.pending_query = sq
                    st.rerun()


# Chat Input
# Handle suggested question click
if st.session_state.pending_query:
    user_input = st.session_state.pending_query
    st.session_state.pending_query = None
else:
    user_input = st.chat_input(
        "Ask anything about GitLab's Handbook or Direction...",
        disabled=not st.session_state.index_ready,
    )

if not st.session_state.index_ready and not user_input:
    st.warning(
        "⚠️ The knowledge base isn't built yet. "
        "Run `python scripts/build_index.py` first, then restart the app.",
        icon="🔧",
    )


# Process Query
if user_input and st.session_state.index_ready:
    st.session_state.messages.append({
        "role":      "user",
        "content":   user_input,
        "timestamp": format_timestamp(),
    })
    st.rerun()

# Check if last message is from user (needs response)
if (
    st.session_state.messages
    and st.session_state.messages[-1]["role"] == "user"
    and st.session_state.index_ready
):
    query = st.session_state.messages[-1]["content"]

    with st.spinner(""):
        # Typing indicator
        typing_placeholder = st.empty()
        typing_placeholder.markdown(
            '<div class="bot-message">'
            '  <div class="bot-avatar">🦊</div>'
            '  <div class="bot-bubble" style="padding: 16px 20px;">'
            '    <span class="typing-dot"></span>'
            '    <span class="typing-dot"></span>'
            '    <span class="typing-dot"></span>'
            '  </div>'
            '</div>',
            unsafe_allow_html=True,
        )

        try:
            # 1. Guardrail check
            from src.guardrails import check_query, get_confidence_label, check_output
            guard = check_query(query)

            if not guard["allowed"]:
                typing_placeholder.empty()
                st.session_state.messages.append({
                    "role":      "assistant",
                    "content":   guard["reason"],
                    "timestamp": format_timestamp(),
                    "sources":   [],
                    "confidence": {"label": "Low", "score": 0},
                    "tokens":    {},
                })
                st.rerun()

            # 2. Retrieve relevant chunks
            retriever = st.session_state.retriever
            chunks = retriever.retrieve(query, top_k=st.session_state.top_k)

            # 3. Confidence scoring
            similarities = [c.get("similarity", 0) for c in chunks]
            confidence   = get_confidence_label(similarities)

            # 4. Build conversation history for multi-turn context
            history = []
            for m in st.session_state.messages[-8:]:
                if m["role"] == "user":
                    history.append({"role": "user", "content": m["content"]})
                elif m["role"] == "assistant":
                    history.append({"role": "model", "content": m["content"]})

            # 5. Generate response
            from src.llm import generate_response
            result = generate_response(
                question=query,
                context_chunks=chunks,
                temperature=st.session_state.temperature,
                conversation_history=history[:-1],  # exclude current turn
            )

            answer = result["answer"]

            # 6. Output safety check
            safety = check_output(answer)
            if not safety["safe"]:
                answer = "I encountered an issue generating a response. Please try rephrasing your question."

            typing_placeholder.empty()

            st.session_state.messages.append({
                "role":       "assistant",
                "content":    answer,
                "timestamp":  format_timestamp(),
                "sources":    chunks,
                "confidence": confidence,
                "suggested_questions": result.get("suggested_questions", []),
                "tokens": {
                    "prompt_tokens":  result.get("prompt_tokens", 0),
                    "output_tokens":  result.get("output_tokens", 0),
                },
            })

        except Exception as e:
            typing_placeholder.empty()
            error_msg = str(e)
            if "API_KEY" in error_msg.upper() or "api_key" in error_msg:
                response_text = (
                    "🔑 **API Key Error**: Please set your `GEMINI_API_KEY` in the `.env` file. "
                    "Get a free key at https://aistudio.google.com"
                )
            elif "quota" in error_msg.lower() or "429" in error_msg or "resource_exhausted" in error_msg.lower():
                response_text = (
                    "⏳ **Rate Limit Hit** — The Gemini API free tier allows 30 requests/minute. "
                    "Automatic retries were exhausted.\n\n"
                    "✅ **Wait 60 seconds and try again** — the limit resets per minute "
                    "and normal chatting uses very few requests."
                )
            else:
                response_text = f"❌ **Error**: {error_msg}\n\nPlease try again or restart the app."

            st.session_state.messages.append({
                "role":       "assistant",
                "content":    response_text,
                "timestamp":  format_timestamp(),
                "sources":    [],
                "confidence": {"label": "Low", "score": 0},
                "tokens":     {},
            })

    st.rerun()
