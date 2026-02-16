# Embedding Score Explainer (Obsidian)

This note explains the score used in:
- `/Users/wuyanjing/PycharmProjects/finance-report-assistant/playground/embedding_retrieval/compare_embeddings.py`

The script reports:
- `neighbor_label_overlap`

---

## 1) Core Similarity: Cosine Similarity

For two chunk vectors $\mathbf{x}$ and $\mathbf{y}$, cosine similarity is:

$$
\text{cosine}(\mathbf{x}, \mathbf{y}) =
\frac{\mathbf{x}\cdot\mathbf{y}}
{\|\mathbf{x}\|\|\mathbf{y}\|}
$$

- Range is approximately $[-1, 1]$.
- Higher value means more similar direction in vector space.
- In this playground, we use cosine to rank nearest neighbors for each chunk.

---

## 2) Reported Metric: Neighbor Label Overlap@K

For each chunk $i$:
1. Compute cosine similarity to all other chunks.
2. Take top-$K$ nearest neighbors.
3. Check whether neighbor section label prefix matches chunk $i$ label prefix (e.g., `Item 1`, `Item 1A`).

Define:
- $N$: number of chunks
- $\mathcal{N}_K(i)$: top-$K$ neighbors of chunk $i$
- $\ell_i$: label prefix for chunk $i$
- Indicator function $\mathbf{1}[\cdot]$ equals 1 if condition true, else 0

Then:

$$
\text{NeighborLabelOverlap@K}
=
\frac{1}{N K}
\sum_{i=1}^{N}
\sum_{j\in \mathcal{N}_K(i)}
\mathbf{1}[\ell_i = \ell_j]
$$

Interpretation:
- Higher value means nearby vectors tend to come from the same section family.
- It is a **coherence proxy** for whether an embedding space groups related filing content.

---

## 3) What This Score Does

- Compares representation families (`bow`, `tfidf`, `hash_embedding`) on the same chunks.
- Gives a fast, model-agnostic signal before expensive end-to-end QA evaluation.
- Helps decide whether a representation is likely useful for semantic retrieval.

---

## 4) Why Use This Score in MVP

1. No hand-labeled relevance dataset required.
2. Cheap to compute on local SEC chunk data.
3. Directionally useful for ranking representation quality in early-stage experiments.

This is ideal for a playground/learning phase where we want fast feedback.

---

## 5) Caveats

1. It is a **proxy metric**, not final task quality.
2. Label-prefix agreement may miss cross-section semantic links.
3. High overlap does not guarantee best answer quality for user Q&A.

Use it together with retrieval metrics like:
- $Hit@K$
- $MRR$

from:
- `/Users/wuyanjing/PycharmProjects/finance-report-assistant/playground/embedding_retrieval/compare_retrievers.py`

---

## 6) Representation Details Used in Script

### BOW

Chunk vector dimension is token count:

$$
x_t = \text{tf}(t, d)
$$

Good lexical baseline, weak semantic generalization.

### TF-IDF

$$
\text{tfidf}(t,d)=\text{tf}(t,d)\cdot\left(\log\frac{1+N}{1+\text{df}(t)}+1\right)
$$

Downweights common terms, usually improves lexical discrimination.

### Hash Embedding (project MVP)

Features (word tokens, character trigrams, bigrams) are hashed into fixed dimension $D$:

$$
h(f)\in\{1,\dots,D\}, \quad s(f)\in\{-1,+1\}
$$

Accumulated vector:

$$
x_{h(f)} \leftarrow x_{h(f)} + s(f)
$$

Then L2-normalized and compared with cosine similarity.

This gives a lightweight dense-ish representation without external model downloads.

