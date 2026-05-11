# ScholarFlow AI

An intelligent **multimodal learning assistant** that transforms raw educational content (PDFs, slides, notes, images) into an **interactive, personalized learning experience** using advanced **RAG (Retrieval-Augmented Generation)** and **LLM-based reasoning**.

---

## Overview

ScholarFlow AI is designed to go beyond traditional Q&A systems by acting as a **true learning companion**. It ingests and understands complex educational materials, builds structured knowledge representations, and supports:

* Context-aware question answering
* Concept-based retrieval
* Personalized explanations
* Adaptive follow-up questions
* Multimodal understanding (text + images + charts)

---

##  Core Features

###  Intelligent Retrieval (Hybrid Search)

* Combines **dense embeddings + sparse retrieval (BM25)**
* Supports **HyDE (Hypothetical Document Embeddings)** for better recall
* Uses **reranking (cross-encoder)** for high-precision results

---

###  Hierarchical Chunking

* Splits documents into:

  * Sections → Paragraphs → Sub-chunks
* Maintains relationships:

  * `parent_chunk_id`
  * `sibling_chunk_ids`

 Enables **small-to-big retrieval** for precise + contextual answers

---

###  Multimodal Understanding

* Handles:

  * Text
  * Images
  * Tables
  * Charts/graphs
* Uses vision-capable LLMs to generate:

  * Image captions
  * Chart interpretations

---

###  Source-Aware Responses

* Every answer includes citations:

```text
Example: "Gradient descent minimizes loss iteratively [Slide 7]"
```

---

###  Adaptive Learning Features

####  Follow-up Questions

Generated across 3 levels:

* Recall
* Conceptual understanding
* Application (real-world)

---

####  Re-Explain Feature

* Student explains a concept
* System:

  * Compares against ground truth
  * Detects gaps
  * Responds Socratically

---

####  Voice Learning Support

* Text-to-Speech with **SSML control**
* Speech-to-Text for student input

---

###  Multilingual Support

* Internal processing in English
* Output translated to user’s preferred language
* Language stored in user profile

---

###  Persistent Learning Memory

* Tracks:

  * Concepts learned
  * Weak areas
* Uses a **knowledge graph** to model:

  * Concept dependencies
  * Learning progression

---

##  System Architecture

```text
                ┌──────────────────────────┐
                │   Document Ingestion     │
                │ (PDF, PPTX, Images, etc)│
                └──────────┬───────────────┘
                           ↓
                ┌──────────────────────────┐
                │  Parsing Layer           │
                │ (Docling / Unstructured) │
                └──────────┬───────────────┘
                           ↓
                ┌──────────────────────────┐
                │  Chunking Engine         │
                │ (Hierarchical)           │
                └──────────┬───────────────┘
                           ↓
        ┌──────────────────────────────────────────┐
        │ Storage Layer                            │
        │                                          │
        │  • Vector DB → Qdrant                    │
        │  • Document Store → MongoDB              │
        │  • Cache → Redis                         │
        │  • Memory Graph → Neo4j                  │
        └──────────────────────────────────────────┘
                           ↓
                ┌──────────────────────────┐
                │ Retrieval Layer          │
                │ Hybrid + HyDE + Rerank   │
                └──────────┬───────────────┘
                           ↓
                ┌──────────────────────────┐
                │ LLM Reasoning Layer      │
                │ (GPT-4o / Claude)        │
                └──────────┬───────────────┘
                           ↓
                ┌──────────────────────────┐
                │ Response Generation      │
                │ + Personalization        │
                └──────────────────────────┘
```
<img width="1155" height="740" alt="ScholarFlow system design" src="https://github.com/user-attachments/assets/723689dd-c611-489d-87ab-112f0a14271d" />

---

##  Metadata Schema

Each chunk contains:

```json
{
  "chunk_id": "uuid",
  "text_content": "...",
  "chunk_type": "text | table | image_caption | formula",
  "page_num": 5,
  "has_image": true,
  "importance_score": 0.85,
  "language_detected": "en",
  "parent_chunk_id": "uuid",
  "sibling_chunk_ids": ["uuid1", "uuid2"]
}
```

---

##  Tech Stack

### Core Components

* **Parser:** Docling / Unstructured.io
* **Embeddings:** OpenAI (`text-embedding-3-large`)
* **Vector DB:** Qdrant
* **Document Store:** MongoDB
* **Cache / Sessions:** Redis
* **Memory Graph:** Neo4j

---

### AI & ML

* **LLM:** GPT-4o / Claude 3.5 Sonnet
* **Reranker:** Cohere Rerank API
* **Speech-to-Text:** Whisper
* **Text-to-Speech:** ElevenLabs / Azure TTS

---

## ⚙️ Installation

```bash
git clone https://github.com/Naden-Mohamed/ScholarFlow-AI.git
cd ScholarFlow-AI

pip install -r requirements.txt
```

---

## ▶️ Usage

```python
# Example flow
1. Upload document
2. System parses & chunks
3. Embeddings stored in Qdrant
4. Ask a question
5. Hybrid retrieval + reranking
6. LLM generates answer with citations
```

---

##  Example Query

```text
User: "Explain gradient descent simply"
```

```text
Response:
Gradient descent is an optimization algorithm used to minimize loss functions [Slide 7].

Follow-up:
- What happens if the learning rate is too high?
- Can you explain it in your own words?
```
---

## 📄 License

MIT License

---
