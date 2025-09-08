# Change_Impact_Analysis_RAG
📄 Change Impact Analysis using RAG + LLaMA

This project is designed to analyze changes between two versions of documents and assess their potential impact. It combines document comparison, semantic search, and AI-powered reasoning to provide a structured change impact analysis.

The workflow is:

Document Comparison – Detects differences between old and new versions, including added, deleted, and modified files.

RAG (Retrieval-Augmented Generation) – Uses semantic search with embeddings (via SentenceTransformers + FAISS) to find related content that may be affected by the changes.

Impact Analysis with LLaMA/Mistral – Generates an AI-driven explanation of the changes, highlighting possible risks, dependencies, and recommendations.

Visualization & Reporting – Results are displayed in a Streamlit dashboard, including change summaries, detailed diffs, and exportable reports (JSON/Markdown).

✨ Features

📂 Upload and compare two document versions (old vs new)

🔎 Detect file-level changes: added, modified, deleted

📊 Show line-level differences with counts of additions/deletions

📖 Provide diff previews for quick inspection

🤖 Perform AI-driven impact analysis using LLaMA/Mistral models

🔗 Retrieve related context documents with semantic search (RAG)

📈 Visualize change distribution with charts

💾 Export results in JSON or Markdown reports

🛠 Tech Stack

Frontend: Streamlit (interactive dashboard)

Backend: FastAPI (REST API for analysis)

Document Comparison: Python difflib

Embeddings: SentenceTransformers (all-MiniLM-L6-v2)

Vector Store: FAISS (for semantic search)

AI Model: LLaMA/Mistral via Hugging Face Transformers

Data Handling: Pandas, JSON, pathlib, tempfile
