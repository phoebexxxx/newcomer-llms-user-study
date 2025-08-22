import os, json
import faiss
import numpy as np
from openai import OpenAI

# load both text & embeddings
def load_index_and_chunks():
    base = os.path.dirname(__file__)
    index = faiss.read_index(os.path.join(base, "faiss.index"))
    with open(os.path.join(base, "text_chunks.json"), "r", encoding="utf-8") as f:
        chunks = json.load(f)
    return index, chunks

# embedding user query
def embed_query(q: str, client: "OpenAI"):
    # keep sync with build script model
    resp = client.embeddings.create(model="text-embedding-3-small", input=[q])
    v = np.array(resp.data[0].embedding, dtype="float32").reshape(1, -1)
    faiss.normalize_L2(v)
    return v


# define the search function
def search(index, chunks, query_vec, top_k=3):
    sims, idxs = index.search(query_vec, top_k)
    out = []
    for j, i in enumerate(idxs[0]):
        if i < 0: 
            continue
        out.append((chunks[i], float(sims[0][j])))
    return out

# tag with source
def format_context(results):
    # compact, source-tagged
    lines = []
    for (doc, score) in results:
        lines.append(f"[{doc['source']}]\n{doc['text']}")
    return "\n\n---\n\n".join(lines)


def make_rag_messages(system_prompt, stage_prompt, history, user_input, context_block):
    # history is a list of {"role": "...", "content": "..."} excluding system
    msgs = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": stage_prompt},
        {"role": "system", "content": (
            "You are a Wikipedia editing assistant. Use the CONTEXT to ground your answer. "
            "Cite the policy names (e.g., NPOV, V, NOR) with actual web links and give actionable steps."
            "If the CONTEXT is irrelevant, simply answer from general Wikipedia policy knowledge."
        )},
        {"role": "system", "content": f"CONTEXT START\n{context_block}\nCONTEXT END"}
    ]
    msgs.extend(history)
    msgs.append({"role": "user", "content": user_input})
    return msgs


