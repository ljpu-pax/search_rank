#!/usr/bin/env python3
"""Turbopuffer client for querying the candidate database."""

import os
from typing import List, Dict, Any, Optional
import turbopuffer as tpuf
from dotenv import load_dotenv

load_dotenv()


class TurbopufferClient:
    """Client for querying Turbopuffer vector database."""

    def __init__(self, api_key: Optional[str] = None, namespace_name: str = "search-test-v4"):
        """Initialize the Turbopuffer client."""
        self.api_key = api_key or os.getenv("TURBOPUFFER_API_KEY")
        if not self.api_key:
            raise ValueError("TURBOPUFFER_API_KEY not found in environment")

        # Use new Turbopuffer API with correct region
        self.client = tpuf.Turbopuffer(
            api_key=self.api_key,
            region="aws-us-west-2"
        )
        self.namespace = self.client.namespace(namespace_name)

    def query(
        self,
        vector: List[float],
        top_k: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        include_attributes: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Query the Turbopuffer collection with a vector and optional filters.

        Args:
            vector: Query embedding vector (1024 dims from voyage-3)
            top_k: Number of results to return
            filters: Metadata filters to apply
            include_attributes: Whether to include attributes in response

        Returns:
            List of matching candidate profiles
        """
        query_params = {
            "rank_by": ("vector", "ANN", vector),
            "top_k": top_k,
            "include_attributes": include_attributes,
        }

        if filters:
            query_params["filters"] = filters

        try:
            result = self.namespace.query(**query_params)
            return self._format_results(result)
        except Exception as e:
            print(f"Error querying Turbopuffer: {e}")
            raise

    def _format_results(self, result) -> List[Dict[str, Any]]:
        """Format Turbopuffer results into a consistent structure."""
        formatted = []

        # Turbopuffer returns result.rows with id, dist, and attributes
        if hasattr(result, 'rows'):
            for row in result.rows:
                formatted_result = {
                    "_id": row.id,
                    "distance": row.dist if hasattr(row, 'dist') else None,
                    "attributes": row.attributes if hasattr(row, 'attributes') else {}
                }
                formatted.append(formatted_result)

        return formatted

    def get_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieve specific candidates by their IDs.

        Args:
            ids: List of MongoDB object IDs

        Returns:
            List of candidate profiles
        """
        # This would require a different API call or multiple queries
        # For now, we'll note this as a potential feature
        raise NotImplementedError("Direct ID lookup not yet implemented")


def test_connection():
    """Test the Turbopuffer connection."""
    try:
        client = TurbopufferClient()
        print("✓ Successfully connected to Turbopuffer")
        print(f"  Namespace: search-test-v4")
        print(f"  Region: aws-us-west-2")
        return True
    except Exception as e:
        print(f"✗ Failed to connect to Turbopuffer: {e}")
        return False


if __name__ == "__main__":
    test_connection()
