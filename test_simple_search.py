#!/usr/bin/env python3
"""Test simple search without filters."""

from turbopuffer_client import TurbopufferClient
from embedding_client import EmbeddingClient

# Initialize clients
tpuf = TurbopufferClient()
embedding = EmbeddingClient()

# Generate embedding for query
query = "tax lawyer with JD degree"
print(f"Query: {query}")

query_vec = embedding.embed_query(query)
print(f"Generated {len(query_vec)}-dim embedding")

# Query without filters first
print("\nQuerying Turbopuffer (no filters)...")
results = tpuf.query(
    vector=query_vec,
    top_k=5,
    include_attributes=True
)

print(f"Found {len(results)} results\n")

# Display results
for i, result in enumerate(results):
    print(f"{i+1}. ID: {result['_id']}")
    print(f"   Distance: {result.get('distance', 'N/A')}")

    attrs = result.get('attributes', {})
    if 'name' in attrs:
        print(f"   Name: {attrs.get('name')}")
    if 'deg_degrees' in attrs:
        print(f"   Degrees: {attrs.get('deg_degrees')}")
    if 'exp_titles' in attrs:
        print(f"   Titles: {attrs.get('exp_titles', [])[:3]}")
    if 'rerankSummary' in attrs:
        summary = attrs['rerankSummary'][:150]
        print(f"   Summary: {summary}...")
    print()
