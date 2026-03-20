# 📄 AskMyFiles

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Ollama](https://img.shields.io/badge/LLM-Ollama-black?style=flat&logo=ollama&logoColor=white)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange?style=flat)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat)

> **Chat with your PDFs. Locally. Privately. For free.**

---

## What is this?

You know that feeling when you have a 60-page PDF and you just need *one* answer from it? You scroll, you search, you Ctrl+F random words hoping to get lucky.

**AskMyFiles fixes that.**

Upload any PDF — a research paper, your resume, a contract, a textbook chapter — and just ask it questions in plain English. It reads the document, understands the context, and gives you a direct answer. No hallucinations from things outside your doc. No API bills. No one else seeing your files.

It's your own private AI assistant for documents, running entirely on your machine.


## How RAG actually works

Most people hear "AI chatbot" and think the LLM has somehow memorized your document. It hasn't. Here's what's actually happening under the hood:

```
YOUR PDF
   │
   ▼
┌─────────────────────────────────────────────┐
│  1. EXTRACT   PyMuPDF pulls raw text        │
│               from every page               │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│  2. CHUNK     Text is split into ~500       │
│               character overlapping pieces  │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│  3. EMBED     Each chunk is converted into  │
│               a vector (list of numbers)    │
│               using nomic-embed-text        │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│  4. STORE     All vectors saved to          │
│               ChromaDB on your machine      │
└─────────────────────────────────────────────┘


YOU ASK A QUESTION
   │
   ▼
┌─────────────────────────────────────────────┐
│  5. EMBED     Your question also becomes    │
│               a vector                      │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│  6. SEARCH    ChromaDB finds the 5 chunks   │
│               most similar to your question │
│               (cosine similarity)           │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│  7. ANSWER    Those chunks + your question  │
│               go into llama3.2 as context.  │
│               The LLM answers using ONLY    │
│               what's in your document.      │
└─────────────────────────────────────────────┘
```

**The magic?** The LLM never sees your whole document at once. It only sees the most relevant pieces. That's why it stays grounded and doesn't make things up.

---

## Why run it locally?

Honestly, I could have just called the OpenAI API and been done in 20 minutes. But I didn't — and here's why that was the right call:

### 🔒 Privacy first
When you upload a PDF to a cloud-based AI tool, that file leaves your machine. It hits a server somewhere. It might be logged, stored, or used for training. For resumes, contracts, medical reports, or anything sensitive — that's not okay. With AskMyFiles, **your files never leave your computer.** Full stop.

### 💸 Zero API costs
OpenAI charges per token. A large PDF can cost you real money, especially if you're testing, iterating, or building on top of it. Running Ollama locally means **infinite queries, zero dollars.**

### 🚀 No rate limits
Cloud APIs throttle you. Local inference doesn't. You can hammer it with 100 questions back to back and nothing breaks.

### 🧠 You actually learn more
When you use an API, it's a black box. When you run a model locally, you understand what an embedding is, why chunking matters, how similarity search works. That knowledge sticks — and it shows in interviews.

---

## Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| LLM | Ollama (llama3.2) | Free, local, fast |
| Embeddings | nomic-embed-text | Best open-source embedding model |
| Vector DB | ChromaDB | Easiest local vector store, persistent |
| PDF Parsing | PyMuPDF (fitz) | Fast and reliable text extraction |
| UI | Streamlit | Fastest way to ship a working ML app |

---

## Project Structure

```
askmyfiles/
├── app.py           # Streamlit UI — sidebar, chat, doc management
├── rag_engine.py    # Core RAG logic — ingest, embed, query, delete
├── requirements.txt # Dependencies
├── README.md
└── chroma_db/       # Auto-created: your local vector store
```

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/askmyfiles.git
cd askmyfiles
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Pull the Ollama models
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```

### 5. Start Ollama
```bash
ollama serve
```

### 6. Run the app
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) and start chatting with your PDFs.

---

## How to Use

1. **Upload** a PDF using the sidebar
2. Click **⚡ INGEST** — this chunks, embeds, and stores your document
3. See the info card showing pages, chunks, file size, and embedding time
4. **Ask anything** about your document in the chat box
5. Click **SEND →** to get your answer
6. Toggle **Show retrieved chunks** to see exactly what context the LLM used
7. Switch between multiple docs using the **Loaded Documents** list
8. Delete any doc with the 🗑 button — removes it from the vector store

---

## Future Improvements

Things I want to add next:

- [ ] **Multi-PDF querying** — ask questions across multiple documents at once
- [ ] **Semantic chunking** — smarter splitting based on meaning, not character count
- [ ] **Conversation memory** — remember previous questions in the same session
- [ ] **FastAPI backend** — decouple the RAG engine from the UI
- [ ] **Pinecone support** — cloud vector store option for deployment
- [ ] **Export chat** — download your Q&A session as a PDF or markdown
- [ ] **Source highlighting** — show exactly which page the answer came from
---

*Built from scratch as part of my AI/ML portfolio. No LangChain. No API keys. Just Python, vectors, and a local LLM.*
