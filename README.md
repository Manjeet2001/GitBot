# 🦊 GitBot — GenAI Chatbot for GitLab Handbook & Direction

> An AI-powered chatbot that lets you explore GitLab's Handbook and Product Direction pages through natural language conversation — built with Google Gemini, RAG, and Streamlit.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **RAG Pipeline** | Retrieves the most relevant GitLab content before generating answers |
| 🛡 **Guardrails** | Multi-layer topic enforcement — only answers GitLab-related questions |
| 📚 **Source Citations** | Every answer shows the GitLab pages used to generate it |
| 🎯 **Confidence Scores** | AI self-rates its answer quality based on source relevance |
| 🔄 **Multi-turn Memory** | Remembers conversation context for follow-up questions |
| 🗄 **Unified Vector Store** | Uses ChromaDB as the robust local database for fast hybrid search |
| 💾 **Export Chat** | Download your full conversation as a text file |
| ⚙️ **Configurable** | Adjust Top-K sources, response creativity, and display options |

---

## 🏗 Architecture

```
User Query
    │
    ▼
┌──────────────────┐
│   Guardrails     │  ← keyword + regex + Gemini classification
│  (guardrails.py) │
└────────┬─────────┘
         │ (allowed)
         ▼
┌──────────────────┐
│    Retriever     │  ← Gemini Embeddings + ChromaDB
│  (retriever.py)  │
└────────┬─────────┘
         │ top-K chunks + similarity scores
         ▼
┌──────────────────┐
│   Gemini LLM     │  ← gemini-1.5-flash with RAG prompt
│    (llm.py)      │
└────────┬─────────┘
         │
         ▼
  Answer + Sources + Confidence Badge → Streamlit UI
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- A **free** Gemini API key → [Google AI Studio](https://aistudio.google.com)

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd RAG
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
GEMINI_API_KEY=your_key_here
```

### 3. Build the Knowledge Index

This scrapes GitLab's Handbook and Direction pages, chunks the text, generates embeddings, and builds the search index. **Run once.**

```bash
python scripts/build_index.py
```

Options:
```bash
python scripts/build_index.py --max-pages 100    # Quick test run (fewer pages)
python scripts/build_index.py --rebuild          # Force full rebuild
```

### 4. Run the Chatbot

```bash
streamlit run app.py
```

Opens at **http://localhost:8501** 🎉

---

> Everyone who visits the deployed URL will use the Streamlit application. Since ChromaDB runs locally, the index is built instantly into the `vectorstore/` directory!

---

## 📁 Project Structure

```
RAG/
├── app.py                   # Streamlit chatbot application
├── requirements.txt         # Python dependencies
├── supabase_setup.sql       # SQL schema for Supabase deployment
├── .env.example             # Environment variable template
├── .streamlit/
│   └── config.toml          # Dark theme configuration
├── scripts/
│   └── build_index.py       # One-command index builder
└── src/
    ├── scraper.py           # GitLab handbook/direction scraper
    ├── chunker.py           # Text chunking with overlap
    ├── embeddings.py        # Gemini embeddings + ChromaDB
    ├── retriever.py         # Similarity search
    ├── llm.py               # Gemini response generation
    └── guardrails.py        # Topic guardrail + confidence scoring
```

---

## 🛡 Bonus Features Implemented

### 1. Multi-Layer Guardrailing
Queries go through **three checks** before hitting the LLM:
- **Keyword fast-path** — 60+ GitLab-specific terms
- **Pattern matching** — regex for obvious off-topic patterns
- **LLM classification** — Gemini classifies ambiguous queries (yes/no)

### 2. Full Transparency
- Every answer shows the exact GitLab Handbook/Direction pages used
- Source relevance percentages shown per source
- Text excerpts from retrieved chunks visible in expandable panel

### 3. Confidence Scoring
- Computed from retrieval similarity scores (weighted average)
- High 🟢 / Medium 🟡 / Low 🔴 badge on every answer
- Explains what the score means to users

### 4. Product UX Enhancements
- Multi-turn conversation with last 3-exchange memory
- Suggested starter questions for new users
- Token usage display (prompt + output tokens)
- Adjustable Top-K and temperature via sidebar
- Export full conversation as text file
- Animated typing indicator during generation

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `GEMINI_API_KEY not set` | Add key to `.env` from [aistudio.google.com](https://aistudio.google.com) |
| `ChromaDB error` | Make sure `python scripts/build_index.py --rebuild` ran completely |
| Scraper too slow | Use `--max-pages 50` for a quick test |

---

## 📄 License

MIT — free for educational use.

---

*Built with ❤️ using Google Gemini, ChromaDB, and Streamlit*
