#!/usr/bin/env python3
"""Re-ranking module for search results."""

from typing import List, Dict, Any, Optional
from sentence_transformers import CrossEncoder
import numpy as np


class Reranker:
    """Re-rank search results using cross-encoder and custom scoring."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize the reranker.

        Args:
            model_name: Name of the cross-encoder model to use
        """
        self.cross_encoder = CrossEncoder(model_name)

    def score_with_cross_encoder(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        text_field: str = "rerankSummary"
    ) -> List[float]:
        """
        Score candidates using cross-encoder.

        Args:
            query: Search query string
            candidates: List of candidate profiles
            text_field: Field to use for scoring (default: rerankSummary)

        Returns:
            List of cross-encoder scores
        """
        # Prepare query-document pairs
        pairs = []
        for candidate in candidates:
            # Extract text from attributes
            attributes = candidate.get("attributes", {})
            text = attributes.get(text_field, "")

            # Fallback: combine education and experience if rerankSummary not available
            if not text:
                education = " ".join(attributes.get("education", []))
                experience = " ".join(attributes.get("experience", []))
                text = f"{education} {experience}"

            pairs.append([query, text])

        # Score with cross-encoder
        if pairs:
            scores = self.cross_encoder.predict(pairs)
            return scores.tolist() if isinstance(scores, np.ndarray) else scores
        return []

    def score_soft_criteria(
        self,
        candidate: Dict[str, Any],
        soft_criteria: List[str]
    ) -> float:
        """
        Score a candidate based on soft criteria (nice-to-haves).

        Args:
            candidate: Candidate profile
            soft_criteria: List of soft criteria strings

        Returns:
            Soft criteria score (0-1)
        """
        attributes = candidate.get("attributes", {})
        score = 0.0
        max_score = len(soft_criteria)

        if max_score == 0:
            return 1.0  # No soft criteria = full score

        # Check each soft criterion
        for criterion in soft_criteria:
            criterion_lower = criterion.lower()

            # Check in rerankSummary
            summary = attributes.get("rerankSummary", "").lower()
            if any(keyword in summary for keyword in criterion_lower.split()):
                score += 1.0
                continue

            # Check in experience
            experience = " ".join(attributes.get("experience", [])).lower()
            if any(keyword in experience for keyword in criterion_lower.split()):
                score += 0.8
                continue

            # Check in titles
            titles = " ".join(attributes.get("exp_titles", [])).lower()
            if any(keyword in titles for keyword in criterion_lower.split()):
                score += 0.6

        return min(score / max_score, 1.0)

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        soft_criteria: Optional[List[str]] = None,
        use_cross_encoder: bool = True,
        cross_encoder_weight: float = 0.6,
        soft_criteria_weight: float = 0.2,
        distance_weight: float = 0.2
    ) -> List[Dict[str, Any]]:
        """
        Re-rank candidates using multiple signals.

        Args:
            query: Search query string
            candidates: List of candidate profiles from initial retrieval
            soft_criteria: Optional list of soft criteria
            use_cross_encoder: Whether to use cross-encoder scoring
            cross_encoder_weight: Weight for cross-encoder score
            soft_criteria_weight: Weight for soft criteria score
            distance_weight: Weight for vector distance score

        Returns:
            Re-ranked list of candidates with scores
        """
        if not candidates:
            return []

        # Get cross-encoder scores
        if use_cross_encoder:
            ce_scores = self.score_with_cross_encoder(query, candidates)
            # Normalize to 0-1
            ce_scores = np.array(ce_scores)
            if ce_scores.max() > ce_scores.min():
                ce_scores = (ce_scores - ce_scores.min()) / (ce_scores.max() - ce_scores.min())
        else:
            ce_scores = np.ones(len(candidates))

        # Get soft criteria scores
        if soft_criteria:
            soft_scores = np.array([
                self.score_soft_criteria(candidate, soft_criteria)
                for candidate in candidates
            ])
        else:
            soft_scores = np.ones(len(candidates))

        # Get distance scores (lower distance = higher score)
        distances = np.array([candidate.get("distance", 0.0) for candidate in candidates])
        if distances.max() > distances.min():
            distance_scores = 1 - (distances - distances.min()) / (distances.max() - distances.min())
        else:
            distance_scores = np.ones(len(candidates))

        # Combine scores
        final_scores = (
            cross_encoder_weight * ce_scores +
            soft_criteria_weight * soft_scores +
            distance_weight * distance_scores
        )

        # Add scores to candidates and sort
        for i, candidate in enumerate(candidates):
            candidate["rerank_score"] = float(final_scores[i])
            candidate["ce_score"] = float(ce_scores[i])
            candidate["soft_score"] = float(soft_scores[i])
            candidate["distance_score"] = float(distance_scores[i])

        # Sort by final score (descending)
        reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)

        return reranked


def test_reranker():
    """Test the reranker."""
    print("Testing Reranker...")

    # Create dummy candidates
    candidates = [
        {
            "_id": "1",
            "distance": 0.5,
            "attributes": {
                "rerankSummary": "Tax attorney with 5 years experience handling IRS audits",
                "deg_degrees": ["jd"],
                "exp_titles": ["attorney", "tax lawyer"]
            }
        },
        {
            "_id": "2",
            "distance": 0.3,
            "attributes": {
                "rerankSummary": "Software engineer with Python experience",
                "deg_degrees": ["bachelor's"],
                "exp_titles": ["software engineer"]
            }
        }
    ]

    query = "Tax lawyer with IRS audit experience"
    soft_criteria = ["IRS audits", "tax implications"]

    reranker = Reranker()
    print("✓ Reranker initialized")

    reranked = reranker.rerank(
        query=query,
        candidates=candidates,
        soft_criteria=soft_criteria
    )

    print(f"\nReranked {len(reranked)} candidates:")
    for i, candidate in enumerate(reranked):
        print(f"  {i+1}. ID: {candidate['_id']}, Score: {candidate['rerank_score']:.3f}")
        print(f"     CE: {candidate['ce_score']:.3f}, Soft: {candidate['soft_score']:.3f}, Dist: {candidate['distance_score']:.3f}")


if __name__ == "__main__":
    test_reranker()
