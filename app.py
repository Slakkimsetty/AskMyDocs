import streamlit as st
import time
from rag_engine import ingest_pdf, query_rag, list_ingested_docs

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AskMyFiles",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}

/* Background */
.stApp {
    background: #0a0a0f;
    color: #e8e8f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f0f1a !important;
    border-right: 1px solid #1e1e3a;
}

/* Hero title */
.hero-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #7c6af7 0%, #a78bfa 50%, #38bdf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
    line-height: 1.2;
}

.hero-sub {
    font-size: 0.85rem;
    color: #6366a0;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.08em;
    margin-bottom: 2rem;
}

/* Stat chips */
.stat-row {
    display: flex;
    gap: 10px;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.stat-chip {
    background: #13132a;
    border: 1px solid #2a2a4a;
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    color: #a78bfa;
    display: flex;
    align-items: center;
    gap: 6px;
}
.stat-chip .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #22d3ee;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* Chat bubbles */
.chat-user {
    background: #1a1a35;
    border: 1px solid #2e2e55;
    border-radius: 12px 12px 4px 12px;
    padding: 14px 18px;
    margin: 12px 0;
    margin-left: 15%;
    font-size: 0.92rem;
    color: #c4c4e8;
    position: relative;
}
.chat-user::before {
    content: "YOU";
    position: absolute;
    top: -10px; right: 12px;
    font-size: 0.6rem;
    font-family: 'Space Mono', monospace;
    color: #7c6af7;
    background: #0a0a0f;
    padding: 0 6px;
    letter-spacing: 0.1em;
}

.chat-bot {
    background: #0d1525;
    border: 1px solid #1e3a5f;
    border-radius: 12px 12px 12px 4px;
    padding: 14px 18px;
    margin: 12px 0;
    margin-right: 15%;
    font-size: 0.92rem;
    color: #d0e8ff;
    position: relative;
    line-height: 1.7;
}
.chat-bot::before {
    content: "AI";
    position: absolute;
    top: -10px; left: 12px;
    font-size: 0.6rem;
    font-family: 'Space Mono', monospace;
    color: #38bdf8;
    background: #0a0a0f;
    padding: 0 6px;
    letter-spacing: 0.1em;
}

/* Context expander styling */
.context-block {
    background: #0c1220;
    border-left: 3px solid #7c6af7;
    padding: 10px 14px;
    border-radius: 0 6px 6px 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: #6366a0;
    margin: 6px 0;
    line-height: 1.6;
}

/* Upload area */
.upload-hint {
    text-align: center;
    padding: 20px;
    border: 1px dashed #2a2a4a;
    border-radius: 10px;
    color: #4a4a7a;
    font-size: 0.82rem;
    font-family: 'Space Mono', monospace;
    margin: 10px 0 20px;
}

/* Input */
.stTextInput > div > div > input {
    background: #0f0f1a !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 8px !important;
    color: #e8e8f0 !important;
    font-family: 'Sora', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 2px rgba(124,106,247,0.15) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #7c6af7, #38bdf8) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.05em !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Divider */
.section-divider {
    border: none;
    border-top: 1px solid #1e1e3a;
    margin: 1.5rem 0;
}

/* Success/info banners */
.stSuccess, .stInfo {
    background: #0d1525 !important;
    border: 1px solid #1e3a5f !important;
    color: #38bdf8 !important;
}

/* Scrollable chat area */
.chat-scroll {
    max-height: 60vh;
    overflow-y: auto;
    padding-right: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_doc" not in st.session_state:
    st.session_state.active_doc = None
if "ingested_docs" not in st.session_state:
    st.session_state.ingested_docs = list_ingested_docs()
if "chunk_count" not in st.session_state:
    st.session_state.chunk_count = 0

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title">📄 Ask<br>MyFiles</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">// LOCAL · PRIVATE · FAST</div>', unsafe_allow_html=True)

    st.markdown('<div class="upload-hint">⬆ Drop a PDF to begin</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

    if uploaded:
        if st.button("⚡ INGEST PDF"):
            with st.spinner("Embedding chunks..."):
                t0 = time.time()
                n  = ingest_pdf(uploaded.read(), uploaded.name)
                elapsed = round(time.time() - t0, 1)
            st.session_state.active_doc  = uploaded.name
            st.session_state.chunk_count = n
            st.session_state.ingested_docs = list_ingested_docs()
            st.session_state.messages = []
            st.success(f"✓ {n} chunks in {elapsed}s")

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # Previously ingested docs
    if st.session_state.ingested_docs:
        st.markdown("**📚 Loaded Docs**")
        for doc in st.session_state.ingested_docs:
            label = f"{'▶ ' if doc == st.session_state.active_doc else ''}{doc}"
            if st.button(label, key=f"doc_{doc}"):
                st.session_state.active_doc = doc
                st.session_state.messages   = []
                st.rerun()

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:0.7rem; color:#3a3a6a; font-family:'Space Mono',monospace; line-height:1.8;">
    MODEL &nbsp;→ llama3.2<br>
    EMBED &nbsp;→ nomic-embed-text<br>
    STORE &nbsp;→ ChromaDB (local)<br>
    FRAMEWORK → LangChain-free
    </div>
    """, unsafe_allow_html=True)

# ── Main area ──────────────────────────────────────────────────────────────────
if st.session_state.active_doc:
    # Stats row
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-chip"><span class="dot"></span> ACTIVE</div>
        <div class="stat-chip">📄 {st.session_state.active_doc}</div>
        <div class="stat-chip">🧩 {st.session_state.chunk_count} chunks</div>
        <div class="stat-chip">💬 {len(st.session_state.messages)//2} turns</div>
    </div>
    """, unsafe_allow_html=True)

    # Chat history
    chat_html = ""
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            chat_html += f'<div class="chat-user">{msg["content"]}</div>'
        else:
            chat_html += f'<div class="chat-bot">{msg["content"]}</div>'

    if chat_html:
        st.markdown(f'<div class="chat-scroll">{chat_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px; color:#2a2a4a; font-family:'Space Mono',monospace; font-size:0.82rem;">
            ┌─────────────────────────────┐<br>
            │  Ask anything about your PDF │<br>
            └─────────────────────────────┘
        </div>
        """, unsafe_allow_html=True)

    # Input row
    col1, col2 = st.columns([5, 1])
    with col1:
        question = st.text_input("", placeholder="Ask a question about your document...", label_visibility="collapsed", key="q_input")
    with col2:
        send = st.button("SEND →")

    show_context = st.toggle("Show retrieved chunks", value=False)

    if send and question.strip():
        st.session_state.messages.append({"role": "user", "content": question})

        with st.spinner("Thinking..."):
            answer, chunks = query_rag(question, st.session_state.active_doc)

        st.session_state.messages.append({"role": "assistant", "content": answer})

        if show_context and chunks:
            with st.expander(f"📎 {len(chunks)} retrieved chunks", expanded=False):
                for i, c in enumerate(chunks):
                    st.markdown(f'<div class="context-block"><strong>chunk {i+1}</strong><br><br>{c}</div>', unsafe_allow_html=True)

        st.rerun()

else:
    # Empty state
    st.markdown("""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:70vh; text-align:center;">
        <div style="font-size:4rem; margin-bottom:1rem;">📄</div>
        <div style="font-family:'Space Mono',monospace; font-size:1.4rem; color:#2a2a5a; margin-bottom:0.5rem;">NO DOCUMENT LOADED</div>
        <div style="font-size:0.8rem; color:#1e1e3a; font-family:'Space Mono',monospace;">Upload a PDF in the sidebar to start chatting</div>
    </div>
    """, unsafe_allow_html=True)