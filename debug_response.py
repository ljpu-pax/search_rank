#!/usr/bin/env python3
"""Debug Turbopuffer response format."""

import turbopuffer as tpuf
from embedding_client import EmbeddingClient
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize
client = tpuf.Turbopuffer(
    api_key=os.getenv("TURBOPUFFER_API_KEY"),
    region="aws-us-west-2"
)
ns = client.namespace("search-test-v4")

# Get embedding
embedding_client = EmbeddingClient()
query_vec = embedding_client.embed_query("tax lawyer")

# Query with include_attributes as list
result = ns.query(
    rank_by=("vector", "ANN", query_vec),
    top_k=2,
    include_attributes=["name", "deg_degrees", "exp_titles", "rerankSummary"]
)

print("Result type:", type(result))
print("Result dir:", [x for x in dir(result) if not x.startswith('_')])
print("\nFirst row:")
if hasattr(result, 'rows') and len(result.rows) > 0:
    row = result.rows[0]
    print("  Row type:", type(row))
    print("  Row id:", row.id)

    # Try to dump the model to see all fields
    print("\n  Row model_dump:")
    row_dict = row.model_dump()
    for key, value in row_dict.items():
        if key not in ['id', 'vector']:
            print(f"    {key}: {value}")

    # Check for attributes in different ways
    if hasattr(row, 'attributes'):
        print("\n  Has row.attributes:", True)

    # Check if attributes are directly on the row
    for attr in ['name', 'deg_degrees', 'exp_titles', 'rerankSummary']:
        if hasattr(row, attr):
            print(f"  row.{attr}:", getattr(row, attr))
