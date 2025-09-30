#!/usr/bin/env python3
"""Evaluation client for submitting results to the Mercor API."""

import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class EvaluationClient:
    """Client for evaluating search results via Mercor API."""

    def __init__(self, email: str = None):
        """
        Initialize the evaluation client.

        Args:
            email: Email address for authorization (from .env if not provided)
        """
        self.email = email or os.getenv("EVAL_EMAIL")
        if not self.email:
            raise ValueError("EVAL_EMAIL not found in environment")

        self.base_url = "https://mercor-dev--search-eng-interview.modal.run"
        self.endpoint = f"{self.base_url}/evaluate"

    def evaluate(
        self,
        config_path: str,
        object_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Submit ranked results for evaluation.

        Args:
            config_path: Name of the .yml config file (e.g., "tax_lawyer.yml")
            object_ids: List of object IDs in ranked order (min 1, max 10)

        Returns:
            API response with evaluation results
        """
        # Validate inputs
        if not object_ids:
            raise ValueError("object_ids cannot be empty")

        if len(object_ids) > 10:
            print(f"Warning: Truncating {len(object_ids)} results to top 10")
            object_ids = object_ids[:10]

        # Prepare request
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.email
        }

        payload = {
            "config_path": config_path,
            "object_ids": object_ids
        }

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=30
            )

            # Check response
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"API returned status {response.status_code}: {response.text}"
                raise Exception(error_msg)

        except requests.exceptions.RequestException as e:
            print(f"Error calling evaluation API: {e}")
            raise

    def evaluate_from_results(
        self,
        config_path: str,
        results: List[Dict[str, Any]],
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Evaluate search results by extracting object IDs.

        Args:
            config_path: Name of the .yml config file
            results: List of candidate results with _id field
            top_k: Number of top results to submit (default: 10)

        Returns:
            API response with evaluation results
        """
        # Extract object IDs
        object_ids = [result["_id"] for result in results[:top_k]]

        return self.evaluate(config_path, object_ids)


def test_evaluation_client():
    """Test the evaluation client."""
    print("Testing EvaluationClient...")

    try:
        client = EvaluationClient()
        print(f"✓ Client initialized with email: {client.email}")
        print(f"  Endpoint: {client.endpoint}")

        # Note: Can't actually test without valid object IDs
        print("\n⚠ Skipping live API test (requires valid object IDs)")

    except ValueError as e:
        print(f"✗ Failed to initialize client: {e}")
        print("  Please set EVAL_EMAIL in .env file")


if __name__ == "__main__":
    test_evaluation_client()
