# Search Re-Ranking Pipeline

End-to-end candidate search and re-ranking system for Mercor's off-platform search data.

## Overview

This system implements a multi-stage search pipeline that:
1. Queries 100-200K user profiles using vector similarity (Turbopuffer + Voyage AI)
2. Filters candidates by hard criteria (must-haves)
3. Re-ranks results using cross-encoder + soft criteria matching
4. Evaluates results via Mercor's API

## Results

### Performance Metrics (Tax Lawyer Query)

| Metric | Baseline | Optimized | Improvement |
|--------|----------|-----------|-------------|
| **Average Final Score** | 39/100 | 48.5/100 | +24% |
| IRS Audit Experience | 3.2/10 | 4.1/10 | +28% |
| Legal Writing | 4.1/10 | 5.2/10 | +27% |
| Corporate Transactions | 4.4/10 | 5.25/10 | +19% |
| Hard Criteria Pass Rate | 100% | 100% | - |

### Hard Criteria Filtering
- Initial candidates: 100
- After filtering: 84 candidates
- Removed: 16 candidates without JD degree

### Top Candidates
1. **Christopher Young** - 80/100 (tax attorney, IRS audits, M&A experience)
2. **Alessandra J. Hunt-Sanchez** - 78.33/100 (IRS tax conciliation, corporate law)
3. **Irene S.** - 60/100 (legal leadership, regulatory experience)

## Architecture

```
Query → Embedding → Vector Search → Hard Filter → Re-ranking → Evaluation
         (Voyage)   (Turbopuffer)     (84/100)    (Enhanced)    (Mercor API)
```

### Components

1. **Turbopuffer Client** (`turbopuffer_client.py`)
   - Queries vector database with 1024-dim embeddings
   - Region: aws-us-west-2
   - Namespace: search-test-v4

2. **Embedding Client** (`embedding_client.py`)
   - Uses Voyage AI's voyage-3 model
   - Generates 1024-dimensional embeddings

3. **Enhanced Reranker** (`enhanced_reranker.py`)
   - Hard criteria filtering (JD + years of experience)
   - Keyword-based soft criteria matching
   - Multi-field scoring (summary, experience, titles, companies)
   - Weights: 50% soft criteria, 30% cross-encoder, 20% distance

4. **Evaluation Client** (`evaluation_client.py`)
   - Submits top-10 results to Mercor API
   - Returns detailed scoring breakdown

5. **Search Pipeline** (`search_pipeline.py`)
   - Orchestrates end-to-end workflow
   - Loads query configs from YAML
   - Handles evaluation and reporting

## Setup

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Create `.env` file:
```bash
TURBOPUFFER_API_KEY=your_key_here
VOYAGE_API_KEY=your_key_here
OAI_KEY=your_key_here
EVAL_EMAIL=your_email@domain.com
```

## Usage

### Run Evaluation

```bash
python run_evaluation.py
```

### Custom Query

```python
from search_pipeline import SearchPipeline

pipeline = SearchPipeline(
    use_reranking=True,
    use_enhanced_reranker=True,
    initial_k=100,
    final_k=10
)

results = pipeline.search(
    query_text="Tax lawyer with IRS experience",
    hard_criteria=["JD degree", "3+ years experience"],
    soft_criteria=["IRS audits", "corporate tax"]
)
```

## Query Configuration

Example YAML (`queries/tax_lawyer.yml`):

```yaml
natural_language: "Seasoned attorney with a JD from a top U.S. law school and over three years of legal practice"

hard_criteria:
  - "JD degree from an accredited U.S. law school"
  - "3+ years of legal practice experience"

soft_criteria:
  - "Experience advising clients on tax implications"
  - "Experience handling IRS audits"
```

## Optimization Strategies

### 1. Enhanced Soft Criteria Matching
- Keyword extraction (removes stop words)
- Multi-field search (summary, experience, titles, companies)
- Weighted scoring by relevance

### 2. Hard Criteria Filtering
- Pre-filters candidates before re-ranking
- Reduces computational cost
- Ensures baseline qualifications

### 3. Adaptive Weights
- Soft criteria: 50% (prioritizes domain expertise)
- Cross-encoder: 30% (semantic relevance)
- Vector distance: 20% (initial retrieval quality)

## Future Improvements

1. **Query Expansion**
   - Expand "IRS audits" → "IRS", "tax disputes", "tax court", "audit defense"
   - Use LLM to generate query variations

2. **Hybrid Search**
   - Combine vector similarity with BM25 keyword search
   - Better handling of specific terms (e.g., "JD", "CPA")

3. **Learning to Rank (LTR)**
   - Train on historical evaluation data
   - Learn optimal feature weights

4. **Turbopuffer Filters**
   - Implement native filter syntax for hard criteria
   - Reduce initial retrieval size

5. **Multi-Query Testing**
   - Test on banker, engineer, and other role queries
   - Optimize for cross-domain performance

## Files

- `turbopuffer_client.py` - Vector database client
- `embedding_client.py` - Query embedding generation
- `enhanced_reranker.py` - Advanced re-ranking with filtering
- `reranker.py` - Baseline cross-encoder reranker
- `filter_builder.py` - Hard criteria filter construction
- `evaluation_client.py` - Mercor API integration
- `search_pipeline.py` - Main orchestration
- `run_evaluation.py` - Evaluation script
- `queries/` - Query configuration files

## License

Proprietary - Mercor Interview Project
