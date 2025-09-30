#!/usr/bin/env python3
"""Enhanced re-ranking with improved soft criteria matching."""

from typing import List, Dict, Any, Optional
from sentence_transformers import CrossEncoder
import numpy as np
import re


class EnhancedReranker:
    """Enhanced reranker with better soft criteria matching and hard criteria filtering."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """Initialize the enhanced reranker."""
        self.cross_encoder = CrossEncoder(model_name)

    def extract_keywords(self, criteria: str) -> List[str]:
        """
        Extract meaningful keywords from criteria string.

        Args:
            criteria: Criteria string (e.g., "Experience handling IRS audits")

        Returns:
            List of keywords
        """
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'may', 'might', 'must', 'can', 'experience', 'advising'
        }

        # Tokenize and filter
        words = re.findall(r'\b\w+\b', criteria.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        return keywords

    def check_hard_criteria(
        self,
        candidate: Dict[str, Any],
        hard_criteria: List[str]
    ) -> bool:
        """
        Check if candidate passes all hard criteria.

        Args:
            candidate: Candidate profile
            hard_criteria: List of hard criteria strings

        Returns:
            True if all hard criteria are met
        """
        attributes = candidate.get("attributes", {})

        for criterion in hard_criteria:
            criterion_lower = criterion.lower()

            # Check for JD degree
            if 'jd' in criterion_lower or 'juris doctor' in criterion_lower or 'law school' in criterion_lower:
                degrees = attributes.get("deg_degrees", [])
                if not any('jd' in str(d).lower() or 'doctor of law' in str(d).lower() for d in degrees):
                    return False

            # Check for years of experience
            if 'year' in criterion_lower and 'experience' in criterion_lower:
                # Extract number of years required
                match = re.search(r'(\d+)\s*\+?\s*year', criterion_lower)
                if match:
                    required_years = int(match.group(1))

                    # Check exp_years buckets
                    exp_years = attributes.get("exp_years", [])
                    if exp_years:
                        # Extract max bucket value
                        max_bucket = 0
                        for bucket in exp_years:
                            if isinstance(bucket, str) and bucket.replace('+', '').isdigit():
                                max_bucket = max(max_bucket, int(bucket.replace('+', '')))

                        if max_bucket < required_years:
                            return False
                    else:
                        # No years data - can't verify
                        pass

        return True

    def score_soft_criteria_enhanced(
        self,
        candidate: Dict[str, Any],
        soft_criteria: List[str]
    ) -> Dict[str, float]:
        """
        Enhanced soft criteria scoring with detailed breakdown.

        Args:
            candidate: Candidate profile
            soft_criteria: List of soft criteria strings

        Returns:
            Dict with overall score and per-criterion scores
        """
        attributes = candidate.get("attributes", {})
        criterion_scores = {}

        for criterion in soft_criteria:
            score = 0.0
            keywords = self.extract_keywords(criterion)

            if not keywords:
                criterion_scores[criterion] = 0.5
                continue

            # Build searchable text
            summary = attributes.get("rerankSummary", "").lower()
            experience = " ".join(attributes.get("experience", [])).lower()
            education = " ".join(attributes.get("education", [])).lower()
            titles = " ".join(attributes.get("exp_titles", [])).lower()
            companies = " ".join(attributes.get("exp_companies", [])).lower()

            # Score based on keyword matches in different fields
            keyword_matches = 0
            total_keywords = len(keywords)

            for keyword in keywords:
                # High value: summary mentions (most relevant)
                if keyword in summary:
                    score += 1.0
                    keyword_matches += 1
                # Medium value: experience or titles
                elif keyword in experience or keyword in titles:
                    score += 0.7
                    keyword_matches += 0.7
                # Lower value: companies or education
                elif keyword in companies or keyword in education:
                    score += 0.4
                    keyword_matches += 0.4

            # Normalize by number of keywords (0-1 range)
            if total_keywords > 0:
                criterion_scores[criterion] = min(keyword_matches / total_keywords, 1.0)
            else:
                criterion_scores[criterion] = 0.0

        # Overall score is average of individual criteria
        overall = np.mean(list(criterion_scores.values())) if criterion_scores else 0.0

        return {
            "overall": overall,
            "breakdown": criterion_scores
        }

    def rerank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        hard_criteria: Optional[List[str]] = None,
        soft_criteria: Optional[List[str]] = None,
        use_cross_encoder: bool = True,
        # Adjusted weights to prioritize soft criteria matching
        cross_encoder_weight: float = 0.3,
        soft_criteria_weight: float = 0.5,
        distance_weight: float = 0.2
    ) -> List[Dict[str, Any]]:
        """
        Enhanced re-ranking with hard criteria filtering and better soft criteria matching.

        Args:
            query: Search query string
            candidates: List of candidate profiles
            hard_criteria: List of hard criteria (must-haves)
            soft_criteria: List of soft criteria (nice-to-haves)
            use_cross_encoder: Whether to use cross-encoder scoring
            cross_encoder_weight: Weight for cross-encoder score
            soft_criteria_weight: Weight for soft criteria score
            distance_weight: Weight for vector distance score

        Returns:
            Re-ranked and filtered list of candidates
        """
        if not candidates:
            return []

        # Step 1: Filter by hard criteria
        if hard_criteria:
            filtered = [c for c in candidates if self.check_hard_criteria(c, hard_criteria)]
            print(f"  → Hard criteria filtering: {len(candidates)} → {len(filtered)} candidates")
            candidates = filtered

        if not candidates:
            return []

        # Step 2: Score with cross-encoder
        if use_cross_encoder:
            pairs = []
            for candidate in candidates:
                attrs = candidate.get("attributes", {})
                text = attrs.get("rerankSummary", "")
                if not text:
                    exp = " ".join(attrs.get("experience", []))
                    edu = " ".join(attrs.get("education", []))
                    text = f"{exp} {edu}"
                pairs.append([query, text])

            ce_scores = self.cross_encoder.predict(pairs)
            ce_scores = np.array(ce_scores)
            # Normalize
            if ce_scores.max() > ce_scores.min():
                ce_scores = (ce_scores - ce_scores.min()) / (ce_scores.max() - ce_scores.min())
        else:
            ce_scores = np.ones(len(candidates))

        # Step 3: Enhanced soft criteria scoring
        soft_scores_list = []
        if soft_criteria:
            for candidate in candidates:
                result = self.score_soft_criteria_enhanced(candidate, soft_criteria)
                candidate["soft_criteria_breakdown"] = result["breakdown"]
                soft_scores_list.append(result["overall"])
            soft_scores = np.array(soft_scores_list)
        else:
            soft_scores = np.ones(len(candidates))

        # Step 4: Distance scores
        distances = np.array([candidate.get("distance", 0.0) for candidate in candidates])
        if distances.max() > distances.min():
            distance_scores = 1 - (distances - distances.min()) / (distances.max() - distances.min())
        else:
            distance_scores = np.ones(len(candidates))

        # Step 5: Combine scores
        final_scores = (
            cross_encoder_weight * ce_scores +
            soft_criteria_weight * soft_scores +
            distance_weight * distance_scores
        )

        # Add scores to candidates
        for i, candidate in enumerate(candidates):
            candidate["rerank_score"] = float(final_scores[i])
            candidate["ce_score"] = float(ce_scores[i])
            candidate["soft_score"] = float(soft_scores[i])
            candidate["distance_score"] = float(distance_scores[i])

        # Sort by final score
        reranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)

        return reranked


def test_enhanced_reranker():
    """Test the enhanced reranker."""
    print("Testing EnhancedReranker...")

    candidates = [
        {
            "_id": "1",
            "distance": 0.5,
            "attributes": {
                "rerankSummary": "Tax attorney with 5 years experience handling IRS audits and advising on tax implications",
                "deg_degrees": ["JD"],
                "exp_titles": ["Tax Attorney"],
                "exp_years": ["5"]
            }
        },
        {
            "_id": "2",
            "distance": 0.3,
            "attributes": {
                "rerankSummary": "Attorney with general legal practice",
                "deg_degrees": ["JD"],
                "exp_titles": ["Attorney"],
                "exp_years": ["3"]
            }
        },
        {
            "_id": "3",
            "distance": 0.4,
            "attributes": {
                "rerankSummary": "Software engineer",
                "deg_degrees": ["Bachelor's"],
                "exp_titles": ["Engineer"],
                "exp_years": ["10"]
            }
        }
    ]

    query = "Tax lawyer with IRS audit experience"
    hard_criteria = ["JD degree", "3+ years of legal practice experience"]
    soft_criteria = ["Experience handling IRS audits", "Experience advising clients on tax implications"]

    reranker = EnhancedReranker()
    print("✓ EnhancedReranker initialized")

    reranked = reranker.rerank(
        query=query,
        candidates=candidates,
        hard_criteria=hard_criteria,
        soft_criteria=soft_criteria
    )

    print(f"\nReranked {len(reranked)} candidates:")
    for i, candidate in enumerate(reranked):
        print(f"\n  {i+1}. ID: {candidate['_id']}")
        print(f"     Final Score: {candidate['rerank_score']:.3f}")
        print(f"     CE: {candidate['ce_score']:.3f}, Soft: {candidate['soft_score']:.3f}, Dist: {candidate['distance_score']:.3f}")
        if "soft_criteria_breakdown" in candidate:
            print(f"     Soft Criteria Breakdown:")
            for crit, score in candidate["soft_criteria_breakdown"].items():
                print(f"       - {crit[:50]}...: {score:.2f}")


if __name__ == "__main__":
    test_enhanced_reranker()
