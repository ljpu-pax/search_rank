#!/usr/bin/env python3
"""Main search pipeline integrating all components."""

import os
import yaml
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from turbopuffer_client import TurbopufferClient
from embedding_client import EmbeddingClient
from filter_builder import FilterBuilder
from reranker import Reranker
from enhanced_reranker import EnhancedReranker
from evaluation_client import EvaluationClient

load_dotenv()


class SearchPipeline:
    """End-to-end search pipeline for candidate retrieval and re-ranking."""

    def __init__(
        self,
        use_reranking: bool = True,
        use_enhanced_reranker: bool = True,
        initial_k: int = 100,
        final_k: int = 10
    ):
        """
        Initialize the search pipeline.

        Args:
            use_reranking: Whether to use re-ranking (default: True)
            use_enhanced_reranker: Whether to use enhanced reranker (default: True)
            initial_k: Number of candidates to retrieve initially
            final_k: Number of final candidates to return
        """
        self.tpuf_client = TurbopufferClient()
        self.embedding_client = EmbeddingClient()
        self.filter_builder = FilterBuilder()
        self.use_reranking = use_reranking
        self.use_enhanced_reranker = use_enhanced_reranker
        self.initial_k = initial_k
        self.final_k = final_k

        if use_reranking:
            if use_enhanced_reranker:
                self.reranker = EnhancedReranker()
            else:
                self.reranker = Reranker()

    def load_query_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load query configuration from YAML file.

        Args:
            config_path: Path to .yml config file

        Returns:
            Query configuration dict
        """
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config

    def search(
        self,
        query_text: str,
        hard_criteria: Optional[List[str]] = None,
        soft_criteria: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute search pipeline.

        Args:
            query_text: Natural language query
            hard_criteria: List of hard criteria (must-haves)
            soft_criteria: List of soft criteria (nice-to-haves)
            filters: Optional pre-built filters

        Returns:
            List of ranked candidates
        """
        print(f"🔍 Searching: {query_text}")

        # Step 1: Generate query embedding
        print("  → Generating query embedding...")
        query_embedding = self.embedding_client.embed_query(query_text)

        # Step 2: Build filters from hard criteria (temporarily disabled for testing)
        # if hard_criteria and not filters:
        #     print(f"  → Building filters from {len(hard_criteria)} hard criteria...")
        #     filters = self.filter_builder.build_filters_from_criteria(hard_criteria)
        #     if filters:
        #         print(f"     Filters: {filters}")
        if hard_criteria:
            print(f"  → Hard criteria noted: {len(hard_criteria)} (filtering via re-ranking)")

        # Step 3: Query Turbopuffer
        print(f"  → Querying Turbopuffer (top_k={self.initial_k})...")
        results = self.tpuf_client.query(
            vector=query_embedding,
            top_k=self.initial_k,
            filters=filters,
            include_attributes=True
        )
        print(f"     Retrieved {len(results)} candidates")

        if not results:
            print("  ⚠ No results found")
            return []

        # Step 4: Re-rank if enabled
        if self.use_reranking and len(results) > 1:
            if self.use_enhanced_reranker:
                print(f"  → Re-ranking with enhanced reranker (hard + soft criteria)...")
                results = self.reranker.rerank(
                    query=query_text,
                    candidates=results,
                    hard_criteria=hard_criteria,
                    soft_criteria=soft_criteria
                )
            else:
                print(f"  → Re-ranking with cross-encoder...")
                results = self.reranker.rerank(
                    query=query_text,
                    candidates=results,
                    soft_criteria=soft_criteria
                )
            print(f"     Re-ranked {len(results)} candidates")

        # Step 5: Return top-k
        final_results = results[:self.final_k]
        print(f"✓ Returning top {len(final_results)} candidates")

        return final_results

    def search_from_config(self, config_path: str) -> List[Dict[str, Any]]:
        """
        Execute search using a query configuration file.

        Args:
            config_path: Path to .yml config file

        Returns:
            List of ranked candidates
        """
        # Load config
        config = self.load_query_config(config_path)

        # Extract components
        query_text = config.get("natural_language", "")
        hard_criteria = config.get("hard_criteria", [])
        soft_criteria = config.get("soft_criteria", [])

        # Execute search
        return self.search(
            query_text=query_text,
            hard_criteria=hard_criteria,
            soft_criteria=soft_criteria
        )

    def evaluate_query(
        self,
        config_path: str,
        email: str = None
    ) -> Dict[str, Any]:
        """
        Search and evaluate for a specific query config.

        Args:
            config_path: Path to .yml config file
            email: Email for evaluation API (optional)

        Returns:
            Evaluation results from API
        """
        print(f"\n{'='*60}")
        print(f"EVALUATING: {config_path}")
        print(f"{'='*60}")

        # Execute search
        results = self.search_from_config(config_path)

        if not results:
            print("✗ No results to evaluate")
            return {"error": "No results found"}

        # Submit for evaluation
        eval_client = EvaluationClient(email=email)
        config_filename = os.path.basename(config_path)

        print(f"\n📊 Submitting {len(results)} results for evaluation...")
        evaluation = eval_client.evaluate_from_results(
            config_path=config_filename,
            results=results,
            top_k=self.final_k
        )

        print(f"✓ Evaluation complete:")
        print(f"  {evaluation}")

        return evaluation


def main():
    """Run the search pipeline on test queries."""
    # Initialize pipeline
    pipeline = SearchPipeline(
        use_reranking=True,
        initial_k=100,
        final_k=10
    )

    # Test with tax lawyer query
    config_path = "queries/tax_lawyer.yml"

    if os.path.exists(config_path):
        results = pipeline.search_from_config(config_path)

        print("\n" + "="*60)
        print("TOP RESULTS:")
        print("="*60)

        for i, result in enumerate(results[:5]):
            print(f"\n{i+1}. ID: {result['_id']}")
            if 'rerank_score' in result:
                print(f"   Score: {result['rerank_score']:.4f}")
            print(f"   Distance: {result.get('distance', 'N/A')}")

            # Show some attributes
            attrs = result.get('attributes', {})
            if 'name' in attrs:
                print(f"   Name: {attrs.get('name')}")
            if 'rerankSummary' in attrs:
                summary = attrs['rerankSummary']
                print(f"   Summary: {summary[:200]}...")

    else:
        print(f"Query config not found: {config_path}")
        print("Please create query configuration files in the queries/ directory")


if __name__ == "__main__":
    main()
