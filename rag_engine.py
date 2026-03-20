import chromadb
from chromadb.config import Settings
import ollama
import fitz  # PyMuPDF
import hashlib
import re

# ── Constants ──────────────────────────────────────────────────────────────────
EMBED_MODEL   = "nomic-embed-text"
LLM_MODEL     = "llama3.2"
CHUNK_SIZE    = 500       # characters
CHUNK_OVERLAP = 100

# ── ChromaDB client (persistent, local) ───────────────────────────────────────
_client = chromadb.PersistentClient(path="./chroma_db")


def _get_collection(name: str):
    return _client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


# ── PDF → chunks ───────────────────────────────────────────────────────────────
def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc   = fitz.open(stream=file_bytes, filetype="pdf")
    pages = [page.get_text() for page in doc]
    return "\n".join(pages)


def chunk_text(text: str) -> list[str]:
    # Clean up whitespace
    text   = re.sub(r"\n{3,}", "\n\n", text).strip()
    chunks = []
    start  = 0
    while start < len(text):
        end   = start + CHUNK_SIZE
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


# ── Embed & store ──────────────────────────────────────────────────────────────
def ingest_pdf(file_bytes: bytes, filename: str) -> int:
    """Extract, chunk, embed and store a PDF. Returns number of chunks stored."""
    collection_name = _safe_collection_name(filename)
    collection      = _get_collection(collection_name)

    text   = extract_text_from_pdf(file_bytes)
    chunks = chunk_text(text)

    ids, embeddings, documents = [], [], []
    for i, chunk in enumerate(chunks):
        chunk_id = hashlib.md5(f"{filename}_{i}_{chunk[:50]}".encode()).hexdigest()
        emb      = ollama.embeddings(model=EMBED_MODEL, prompt=chunk)["embedding"]
        ids.append(chunk_id)
        embeddings.append(emb)
        documents.append(chunk)

    if ids:
        collection.upsert(ids=ids, embeddings=embeddings, documents=documents)

    return len(chunks)


# ── Query ──────────────────────────────────────────────────────────────────────
def query_rag(question: str, filename: str, top_k: int = 5) -> tuple[str, list[str]]:
    """Return (answer, retrieved_chunks)."""
    collection_name = _safe_collection_name(filename)
    collection      = _get_collection(collection_name)

    # Embed the question
    q_emb = ollama.embeddings(model=EMBED_MODEL, prompt=question)["embedding"]

    # Retrieve top-k relevant chunks
    results = collection.query(query_embeddings=[q_emb], n_results=top_k)
    chunks  = results["documents"][0] if results["documents"] else []

    if not chunks:
        return "I couldn't find relevant information in the document.", []

    context = "\n\n---\n\n".join(chunks)
    prompt  = f"""You are a helpful assistant. Answer the user's question using ONLY the context below.
If the answer is not in the context, say "I don't have enough information in this document to answer that."

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    answer = response["message"]["content"]
    return answer, chunks


# ── Helpers ────────────────────────────────────────────────────────────────────
def _safe_collection_name(filename: str) -> str:
    # Remove extension
    name = filename.replace(".pdf", "").replace(".PDF", "")
    # Replace any non-alphanumeric characters (except _ and -) with underscore
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    # Collapse multiple consecutive underscores into one
    name = re.sub(r"_+", "_", name)
    # Remove leading and trailing underscores
    name = name.strip("_")
    # Truncate to 60 characters
    name = name[:60]
    # Must start with a letter — prefix with "doc_" if not
    if not name or not name[0].isalpha():
        name = "doc_" + name
    # Final fallback
    return name or "default_collection"


def list_ingested_docs() -> list[str]:
    return [c.name for c in _client.list_collections()]