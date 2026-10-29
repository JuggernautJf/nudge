# Nudge 🚀💼

*Tinder for Jobs: Fast, intuitive, and algorithm-driven career matching powered by vector search.*

Welcome to the official repository for **Nudge**. This project explores modern recommendation systems by combining semantic vector search with machine learning pipelines, mimicking how large-scale platforms handle intelligent item retrieval and matching.

## 🗺️ Development Pipeline & Stages

We are tackling this project step-by-step through a rigorous data science and backend engineering pipeline:

1. **Phase 1: Data Ingestion (Scraping)**
   * Gathering a clean, localized set of job listings (Titles, Descriptions, Companies, Locations) using polite scraping scripts or open datasets.

2. **Phase 2: Vector Embeddings (Sentence-Transformers)**
   * Passing raw job descriptions through Hugging Face transformer models (`sentence-transformers`) to convert text into high-dimensional semantic vectors.

3. **Phase 3: Indexing & Retrieval (FAISS)**
   * Loading job vectors into a **FAISS** (Facebook AI Similarity Search) index to enable high-speed Approximate Nearest Neighbor (ANN) querying and similarity matching.

4. **Phase 4: API & Backend Serving (FastAPI)**
   * Serving predictions and custom recommendations via a robust **FastAPI** backend that computes user preference vectors on the fly.

## 🛠️ Tech Stack

* **Data Science & ML:** Python, Pandas, Hugging Face `sentence-transformers`, FAISS (Meta AI)
* **Backend API:** FastAPI, Uvicorn, Pydantic
* **Frontend (Future Scope):** Next.js, Tailwind CSS, Framer Motion (for smooth swipe cards)
* **Data Storage:** Local JSON / SQLite + serialized FAISS vector index files

## 📁 Project Structure

```text
nudge/
├── scraper/            # Python scripts for gathering job data
├── ml_pipeline/        # Embedding generation & FAISS index builder
├── backend/            # FastAPI server & recommendation endpoints
└── README.md
```

## 🚀 Getting Started (Step-by-Step)

### Prerequisites

* Python 3.10+

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/nudge.git
cd nudge
```

### 2. Set Up the Python Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the Data Pipeline

* **Step A (Scrape/Gather Data):** Run your ingestion script to populate raw job data.
* **Step B (Generate Embeddings & FAISS Index):**
  ```bash
  python ml_pipeline/build_index.py
  ```
* **Step C (Start the FastAPI Backend):**
  ```bash
  cd backend
  uvicorn main:app --reload
  ```

## ⚖️ Legal & Data Ethics Note

This project is built strictly for **educational and portfolio purposes**. All scraping scripts adhere to strict rate-limiting, respect `robots.txt`, and avoid harvesting personally identifiable information (PII).

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.