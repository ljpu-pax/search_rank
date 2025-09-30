#!/usr/bin/env python3
"""Voyage AI client for generating embeddings."""

import os
from typing import List, Union
import voyageai
from dotenv import load_dotenv

load_dotenv()


class EmbeddingClient:
    """Client for generating embeddings using Voyage AI."""

    def __init__(self, api_key: str = None):
        """Initialize the Voyage AI client."""
        self.api_key = api_key or os.getenv("VOYAGE_API_KEY")
        if not self.api_key:
            raise ValueError("VOYAGE_API_KEY not found in environment")

        self.client = voyageai.Client(api_key=self.api_key)
        self.model = "voyage-3"

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query.

        Args:
            query: Query text to embed

        Returns:
            1024-dimensional embedding vector
        """
        try:
            response = self.client.embed(query, model=self.model)
            return response.embeddings[0]
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of 1024-dimensional embedding vectors
        """
        try:
            response = self.client.embed(texts, model=self.model)
            return response.embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            raise


def test_embedding():
    """Test the Voyage AI embedding client."""
    try:
        client = EmbeddingClient()

        # Test single query
        test_query = "software engineer with Python experience"
        embedding = client.embed_query(test_query)

        print("✓ Successfully generated embedding")
        print(f"  Model: voyage-3")
        print(f"  Query: {test_query}")
        print(f"  Embedding dimensions: {len(embedding)}")
        print(f"  First 5 values: {embedding[:5]}")

        return True
    except Exception as e:
        print(f"✗ Failed to generate embedding: {e}")
        return False


if __name__ == "__main__":
    test_embedding()
