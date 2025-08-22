import os, json, re, glob
import faiss
import numpy as np
from openai import OpenAI

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "policies")
OUT_DIR  = os.path.join(os.path.dirname(__file__))
EMBED_MODEL = "text-embedding-3-small"

#client = openai.OpenAI(api_key="sk-proj-...")  # Replace with your API key

# read docs from policies directory
def read_docs():
    docs = []
    for path in glob.glob(os.path.join(DATA_DIR, "*.txt")):
        with open(path, "r", encoding="utf-8") as f:
            docs.append({"source": os.path.basename(path), "text": f.read()})
    return docs

def chunk_text(content):
    chunks = []
    pattern = r"\[[^\]]+\]"

    # remove all citations marks from content
    content = re.sub(pattern, "", content)

    # Simple split on triple newlines
    chunks = content.split("\n\n\n")
    print(len(chunks))
    return chunks


def embed_texts(texts):
    # OpenAI Embeddings API (returns 1536-d vectors for text-embedding-3-small)
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return np.array([d.embedding for d in resp.data], dtype="float32")


# step 1: read documents and chunk 
os.makedirs(OUT_DIR, exist_ok=True)
docs = read_docs()
text_chunks = []
for d in docs:
    for ch in chunk_text(d["text"]):
        text_chunks.append({"source": d["source"], "text": ch})

# batch to avoid long payloads
embs = []
B = 64
for i in range(0, len(text_chunks), B):
    batch = [c["text"] for c in text_chunks[i:i+B]]
    embs.append(embed_texts(batch))

X = np.vstack(embs)

# cosine similarity via inner product on normalized vectors
faiss.normalize_L2(X)
index = faiss.IndexFlatIP(X.shape[1])
index.add(X)

faiss.write_index(index, os.path.join(OUT_DIR, "faiss.index"))
with open(os.path.join(OUT_DIR, "text_chunks.json"), "w", encoding="utf-8") as f:
    json.dump(text_chunks, f, ensure_ascii=False, indent=2)

print(f"Built index with {len(text_chunks)} chunks, dim={X.shape[1]}")


